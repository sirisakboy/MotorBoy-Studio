// คนขับคุมเส้นทาง - Main Router
import { getHTMLContent } from "./ui-template";
import { runMotorBoyAI, ChatPayload } from "./ai-service";

export interface Env {
  AI: any;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // ด่านที่ 1: เรียกหน้าจอ UI แชท (GET)
    if (request.method === "GET") {
      return new Response(getHTMLContent(), {
        headers: { "content-type": "text/html;charset=UTF-8" },
      });
    }

    // ด่านที่ 2: จัดการระบบยิงข้อมูลแชทส่ง AI (POST)
    if (request.method === "POST" && url.pathname === "/api/chat") {
      try {
        const payload = (await request.json()) as ChatPayload;

        // เรียกใช้งาน Service สมองกลที่แยกไฟล์ไว้
        const stream = await runMotorBoyAI(payload, env);

        return new Response(stream, {
          headers: { 
            "content-type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
          },
        });
      } catch (err: any) {
        return new Response(JSON.stringify({ error: err.message }), {
          status: 500,
          headers: { "content-type": "application/json" },
        });
      }
    }

    // ด่านที่ 3: เส้นทางอื่นไม่พบขั้วไฟ
    return new Response("Not Found", { status: 404 });
  },
} satisfies ExportedHandler<Env>;