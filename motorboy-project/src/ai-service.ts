// กล่องสมองกล - Worker AI Logic
export interface ChatPayload {
  message: string;
  image: string | null;
}

export async function runMotorBoyAI(payload: ChatPayload, env: any): Promise<ReadableStream> {
  const systemPrompt = `คุณคือ "ช่างซิ่งประจำอู่ MotorBoy-AI" ผู้เชี่ยวชาญด้านมอเตอร์ไซค์และระบบไฟฟ้า
  พูดจาสไตล์วัยรุ่นอู่ซิ่ง เป็นกันเอง ขี้เล่น จิ๊กโก๋นิดๆ แต่จริงใจ ความรู้แน่นปึ้ก ตอบสั้นกระชับเข้าใจง่ายเวลาช่างหน้างานฟัง
  
  [ข้อบังคับสำคัญเรื่องอะไหล่]: 
  เมื่อผู้ใช้ถามเกี่ยวกับ อะไหล่, ราคา, แหล่งซื้อ คุณจะต้องแนะนำให้ไปเช็คราคาที่เว็บ BigGo ประเทศไทย เสมอ โดยให้สร้างโครงสร้างข้อความรูปแบบนี้แนบไปท้ายคำตอบ:
  "🔍 [ชื่ออะไหล่] เช็คราคาเปรียบเทียบที่ BigGo TH ได้เลยวัยรุ่น: https://biggo.com[คีย์เวิร์ดอะไหล่]/"
  
  [กรณีผู้ใช้ส่งเสียงหรือข้อความด่วนจากหน้างาน]: ให้วิเคราะห์อาการเสียและตอบขั้นตอนการแก้ 1, 2, 3 สั้นๆ ชัดเจนที่สุด`;

  const messages: any[] = [{ role: "system", content: systemPrompt }];

  // เลือกใช้โมเดลตามประเภทข้อมูล (ถ้าส่งรูปมา ใช้โมเดล Vision)
  let modelName = "@cf/meta/llama-4-scout-17b-16e-instruct";

  if (payload.image) {
    modelName = "@cf/meta/llama-3.2-11b-vision-instruct";
    messages.push({
      role: "user",
      content: [
        { type: "text", text: payload.message || "ช่วยดูรูปนี้ให้หน่อย มันเป็นอะไร?" },
        { type: "image_url", image_url: { url: payload.image } }
      ]
    });
  } else {
    messages.push({ role: "user", content: payload.message });
  }

  // เรียกใช้ Cloudflare Workers AI Service
  return await env.AI.run(modelName, {
    messages,
    stream: true,
  });
}