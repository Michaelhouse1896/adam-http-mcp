#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";
import { randomUUID } from "node:crypto";
import { z } from "zod";
import { tools, ToolDef } from "./tools.js";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const BASE_URL = process.env.ADAM_BASE_URL || "";
const API_TOKEN = process.env.ADAM_API_TOKEN || "";
const VERIFY_SSL = (process.env.ADAM_VERIFY_SSL || "true").toLowerCase() !== "false";
const DATAQUERY_PUPILS_SECRET = process.env.ADAM_DATAQUERY_PUPILS_SECRET || "";
const DATAQUERY_FAMILIES_SECRET = process.env.ADAM_DATAQUERY_FAMILIES_SECRET || "";
const DATAQUERY_STAFF_SECRET = process.env.ADAM_DATAQUERY_STAFF_SECRET || "";
const PORT = parseInt(process.env.PORT || "3000", 10);

// ---------------------------------------------------------------------------
// Per-session credentials (headers override env vars)
// ---------------------------------------------------------------------------

interface Credentials {
  apiToken: string;
  baseUrl: string;
  dataqueryPupilsSecret: string;
  dataqueryFamiliesSecret: string;
  dataqueryStaffSecret: string;
}

function getCredentials(req: express.Request): Credentials {
  return {
    apiToken: (req.headers['x-adam-api-token'] as string) || API_TOKEN,
    baseUrl: (req.headers['x-adam-base-url'] as string) || BASE_URL,
    dataqueryPupilsSecret: (req.headers['x-adam-dataquery-pupils-secret'] as string) || DATAQUERY_PUPILS_SECRET,
    dataqueryFamiliesSecret: (req.headers['x-adam-dataquery-families-secret'] as string) || DATAQUERY_FAMILIES_SECRET,
    dataqueryStaffSecret: (req.headers['x-adam-dataquery-staff-secret'] as string) || DATAQUERY_STAFF_SECRET,
  };
}

function validateConfig(): void {
  const warnings: string[] = [];
  if (!API_TOKEN) warnings.push("ADAM_API_TOKEN is not set (will require x-adam-api-token header)");
  else if (API_TOKEN.length !== 30) warnings.push("ADAM_API_TOKEN must be exactly 30 characters");
  if (!BASE_URL) warnings.push("ADAM_BASE_URL is not set (will require x-adam-base-url header)");
  else if (!BASE_URL.startsWith("http://") && !BASE_URL.startsWith("https://"))
    warnings.push("ADAM_BASE_URL must start with http:// or https://");
  if (warnings.length > 0) {
    console.warn("Configuration warnings:", warnings.join("; "));
  }
}

// ---------------------------------------------------------------------------
// Zod schema builder (credential-independent)
// ---------------------------------------------------------------------------

function buildZodShape(tool: ToolDef): Record<string, z.ZodTypeAny> {
  const shape: Record<string, z.ZodTypeAny> = {};
  for (const param of tool.params) {
    let field: z.ZodTypeAny =
      param.type === "number" ? z.number().describe(param.description) : z.string().describe(param.description);
    if (!param.required) field = field.optional();
    shape[param.name] = field;
  }
  return shape;
}

// ---------------------------------------------------------------------------
// MCP server factory (closured over per-session credentials)
// ---------------------------------------------------------------------------

function createServer(creds: Credentials): McpServer {
  // -- ADAM API client (uses session credentials) --

  async function adamRequest(
    module: string,
    resource: string,
    params: string[] = []
  ): Promise<any> {
    const parts = [creds.baseUrl, module, resource, ...params.map(encodeURIComponent)];
    const url = parts.join("/");

    const res = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${creds.apiToken}`,
        "Content-Type": "application/json",
      },
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status}: ${text}`);
    }

    const json = await res.json();

    // Unwrap ADAM's response wrapper
    if (json && typeof json === "object" && "response" in json) {
      const inner = (json as any).response;
      if (inner.code !== 200) {
        throw new Error(inner.error || `ADAM API error: code ${inner.code}`);
      }
      return (json as any).data ?? json;
    }

    return json;
  }

  // -- Simple tool executor --

  async function callSimpleTool(tool: ToolDef, args: Record<string, any>): Promise<any> {
    const pathSegments: string[] = [];
    for (const paramName of tool.pathParams || []) {
      const val = args[paramName];
      if (val !== undefined && val !== null && val !== "") {
        pathSegments.push(String(val));
      }
    }
    return adamRequest(tool.module!, tool.resource!, pathSegments);
  }

  // -- Custom tool handlers --

  async function handlePupilsFind(args: Record<string, any>): Promise<any> {
    if (!creds.dataqueryPupilsSecret) throw new Error("ADAM_DATAQUERY_PUPILS_SECRET not configured");
    const data = await adamRequest("dataquery", "get", [creds.dataqueryPupilsSecret]);
    const searchWords = String(args.name).toLowerCase().trim().split(/\s+/);
    const results: any[] = [];
    for (const key of Object.keys(data)) {
      const record = data[key];
      const lastName = (record.last_name_2 || "").toLowerCase();
      const preferredName = (record.preferred_name_3 || "").toLowerCase();
      const fullFirstNames = (record.full_first_names_4 || "").toLowerCase();
      const combined = `${lastName} ${preferredName} ${fullFirstNames}`;
      if (searchWords.every((w: string) => combined.includes(w))) {
        results.push({
          pupil_id: record.adam_id_257,
          admin_number: record.admin_number_1,
          last_name: record.last_name_2,
          preferred_name: record.preferred_name_3,
          full_first_names: record.full_first_names_4,
          grade: record.grade_9,
          email: record.email_21,
        });
      }
    }
    return results;
  }

  async function handleFamiliesFind(args: Record<string, any>): Promise<any> {
    if (!creds.dataqueryFamiliesSecret) throw new Error("ADAM_DATAQUERY_FAMILIES_SECRET not configured");
    const data = await adamRequest("dataquery", "get", [creds.dataqueryFamiliesSecret]);
    const searchWords = String(args.name).toLowerCase().trim().split(/\s+/);
    const results: any[] = [];
    for (const key of Object.keys(data)) {
      const record = data[key];
      const familySurname = (record.family_greeting_surname_133 || "").toLowerCase();
      const familyFirstNames = (record.family_greeting_first_names_143 || "").toLowerCase();
      const addressName = (record.family_address_name_132 || "").toLowerCase();
      const fatherGreeting = (record.father_039_s_greeting_288 || "").toLowerCase();
      const motherGreeting = (record.mother_039_s_greeting_289 || "").toLowerCase();
      const combined = `${familySurname} ${familyFirstNames} ${addressName} ${fatherGreeting} ${motherGreeting}`;
      if (searchWords.every((w: string) => combined.includes(w))) {
        results.push({
          family_id: record.family_identifier_253,
          family_surname: record.family_greeting_surname_133,
          family_first_names: record.family_greeting_first_names_143,
          address_name: record.family_address_name_132,
          father_greeting: record.father_039_s_greeting_288,
          mother_greeting: record.mother_039_s_greeting_289,
        });
      }
    }
    return results;
  }

  async function handleStaffFind(args: Record<string, any>): Promise<any> {
    if (!creds.dataqueryStaffSecret) throw new Error("ADAM_DATAQUERY_STAFF_SECRET not configured");
    const data = await adamRequest("dataquery", "get", [creds.dataqueryStaffSecret]);
    const searchWords = String(args.name).toLowerCase().trim().split(/\s+/);
    const results: any[] = [];
    for (const key of Object.keys(data)) {
      const record = data[key];
      const lastName = (record.last_name_31 || "").toLowerCase();
      const preferredName = (record.first_name_preferred_32 || "").toLowerCase();
      const fullName = (record.full_first_name_142 || "").toLowerCase();
      const combined = `${lastName} ${preferredName} ${fullName}`;
      if (searchWords.every((w: string) => combined.includes(w))) {
        results.push({
          staff_id: record.adam_identifier_284,
          admin_no: record.admin_no_30,
          last_name: record.last_name_31,
          preferred_name: record.first_name_preferred_32,
          full_name: record.full_first_name_142,
          position: record.position_233,
          department: record.department_49,
          email: record.email_address_67,
        });
      }
    }
    return results;
  }

  async function handleClassesList(args: Record<string, any>): Promise<any> {
    const regsRaw = await adamRequest("registrations", "grade", [String(args.grade)]);
    const regs = Array.isArray(regsRaw) ? regsRaw : (regsRaw?.data ?? []);
    if (!Array.isArray(regs)) return [];

    const classes: Record<string, any> = {};
    for (const reg of regs) {
      const desc = reg.class_description || "";
      if (!classes[desc]) {
        classes[desc] = {
          class_description: desc,
          class_id: reg.class_id,
          subject: reg.subject_name || "",
          pupil_count: 0,
        };
      }
      classes[desc].pupil_count += 1;
    }
    return Object.values(classes).sort((a: any, b: any) =>
      a.class_description.localeCompare(b.class_description)
    );
  }

  async function handleClassesParentEmails(args: Record<string, any>): Promise<any> {
    const grade = String(args.grade);
    const classDescription = String(args.class_description);

    const regsRaw = await adamRequest("registrations", "grade", [grade]);
    const regs = Array.isArray(regsRaw) ? regsRaw : (regsRaw?.data ?? []);
    if (!Array.isArray(regs)) throw new Error(`Unexpected registrations format`);

    const searchTerm = classDescription.toLowerCase().trim();
    const matchingRegs: any[] = [];
    const seenPupils = new Set<string>();

    for (const reg of regs) {
      const desc = (reg.class_description || "").toLowerCase();
      const pupilId = reg.pupil_id;
      if (desc.includes(searchTerm) && !seenPupils.has(String(pupilId))) {
        matchingRegs.push(reg);
        seenPupils.add(String(pupilId));
      }
    }

    if (matchingRegs.length === 0) {
      return {
        pupils: [],
        all_emails: [],
        summary: {
          total_pupils: 0,
          total_families: 0,
          total_emails: 0,
          class_description: classDescription,
          grade,
        },
      };
    }

    const pupilsData: any[] = [];
    const allEmailsSet = new Set<string>();

    for (const reg of matchingRegs) {
      const pupilId = reg.pupil_id;
      const pupilInfo: any = {
        pupil_id: pupilId,
        pupil_firstname: reg.pupil_firstname,
        pupil_lastname: reg.pupil_lastname,
        pupil_admin: reg.pupil_admin,
        class_description: reg.class_description,
        families: [],
      };

      try {
        const familyRelsRaw = await adamRequest("familyrelationships", "pupil", [String(pupilId)]);
        const familyRels = Array.isArray(familyRelsRaw)
          ? familyRelsRaw
          : (familyRelsRaw?.data ?? familyRelsRaw);
        if (!Array.isArray(familyRels)) continue;

        for (const familyRel of familyRels) {
          const familyId = familyRel.family_id;
          if (!familyId) continue;
          try {
            const emailsData = await adamRequest("families", "email", [String(familyId)]);
            const emails = Array.isArray(emailsData) ? emailsData : [];
            pupilInfo.families.push({
              family_id: familyId,
              relationship: familyRel.relationship,
              family_name: `${familyRel.family_primary_firstname || ""} ${familyRel.family_primary_lastname || ""}`.trim(),
              emails,
            });
            for (const email of emails) {
              if (email) allEmailsSet.add(String(email).trim());
            }
          } catch {
            // Skip families where email lookup fails
          }
        }
      } catch {
        // Skip pupils where family lookup fails
      }

      pupilsData.push(pupilInfo);
    }

    const totalFamilies = pupilsData.reduce((sum: number, p: any) => sum + p.families.length, 0);
    const matchedClassNames = [...new Set(matchingRegs.map((r: any) => r.class_description))];

    return {
      pupils: pupilsData,
      all_emails: [...allEmailsSet].sort(),
      summary: {
        total_pupils: pupilsData.length,
        total_families: totalFamilies,
        total_emails: allEmailsSet.size,
        class_description: classDescription,
        grade,
        matched_class_names: matchedClassNames,
      },
    };
  }

  async function handleLeavesApproved(args: Record<string, any>): Promise<any> {
    const params: string[] = [];
    if (args.pupil_id) params.push(String(args.pupil_id));

    let data = await adamRequest("leaves", "approved", params);
    if (!Array.isArray(data)) return data;

    const startDate = args.start_date ? String(args.start_date) : null;
    const endDate = args.end_date ? String(args.end_date) : null;

    if (startDate || endDate) {
      data = data.filter((leave: any) => {
        const out = (leave.leave_request_out || "").substring(0, 10);
        if (startDate && out < startDate) return false;
        if (endDate && out > endDate) return false;
        return true;
      });
    }

    return data;
  }

  // -- Dispatch map for custom handlers --

  const customHandlers: Record<string, (args: Record<string, any>) => Promise<any>> = {
    pupils_find: handlePupilsFind,
    families_find: handleFamiliesFind,
    staff_find: handleStaffFind,
    classes_list: handleClassesList,
    classes_parent_emails: handleClassesParentEmails,
    leaves_approved: handleLeavesApproved,
  };

  // -- Register tools --

  const server = new McpServer({
    name: "adam-school-mis",
    version: "1.0.0",
  });

  for (const tool of tools) {
    const shape = buildZodShape(tool);

    server.tool(tool.toolName, tool.description, shape, async (args: any) => {
      try {
        let result: any;
        if (tool.handler === "custom") {
          const handler = customHandlers[tool.toolName];
          if (!handler) throw new Error(`No custom handler for ${tool.toolName}`);
          result = await handler(args);
        } else {
          result = await callSimpleTool(tool, args);
        }
        return {
          content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }],
        };
      } catch (err: any) {
        return {
          content: [{ type: "text" as const, text: `Error: ${err.message}` }],
          isError: true,
        };
      }
    });
  }

  return server;
}

// ---------------------------------------------------------------------------
// Express HTTP transport
// ---------------------------------------------------------------------------

async function main() {
  validateConfig();

  const app = express();
  app.use(express.json());

  const sessions = new Map<
    string,
    { transport: StreamableHTTPServerTransport; server: McpServer }
  >();

  // POST /mcp — initialize session or forward tool calls
  app.post("/mcp", async (req, res) => {
    const sessionId = req.headers["mcp-session-id"] as string | undefined;

    if (sessionId && sessions.has(sessionId)) {
      const session = sessions.get(sessionId)!;
      await session.transport.handleRequest(req, res, req.body);
      return;
    }

    if (sessionId && !sessions.has(sessionId)) {
      res.status(400).json({ error: "Invalid session ID" });
      return;
    }

    // New session — read credentials from headers (falling back to env vars)
    const creds = getCredentials(req);
    const server = createServer(creds);

    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: () => randomUUID(),
      onsessioninitialized: (id) => {
        sessions.set(id, { transport, server });
        console.log(`Session started: ${id}`);
      },
    });

    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  });

  // GET /mcp — SSE for server → client notifications
  app.get("/mcp", async (req, res) => {
    const sessionId = req.headers["mcp-session-id"] as string | undefined;
    if (!sessionId || !sessions.has(sessionId)) {
      res.status(400).json({ error: "Invalid or missing session ID" });
      return;
    }
    await sessions.get(sessionId)!.transport.handleRequest(req, res);
  });

  // DELETE /mcp — close and cleanup session
  app.delete("/mcp", async (req, res) => {
    const sessionId = req.headers["mcp-session-id"] as string | undefined;
    if (!sessionId || !sessions.has(sessionId)) {
      res.status(400).json({ error: "Invalid or missing session ID" });
      return;
    }
    const session = sessions.get(sessionId)!;
    await session.transport.handleRequest(req, res);
    await session.server.close();
    sessions.delete(sessionId);
    console.log(`Session closed: ${sessionId}`);
  });

  app.listen(PORT, () => {
    console.log(`ADAM MCP server listening on http://0.0.0.0:${PORT}/mcp`);
  });
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
