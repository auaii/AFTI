import os
from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from testing_protocol_agent.testing_agent import test_protocol_agent
from defect_analysis_agent.defect_agent import defect_analysis_agent
# formats messages
from utils import show_prompt, format_messages

load_dotenv()

# Model Gemini3
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)

subagents = [test_protocol_agent, defect_analysis_agent]

supervisor_system_prompt = """
You are the **PCB Project Supervisor**, an expert Project Manager responsible for orchestrating specialized Subagents to analyze PCB defects and generate final reports. 
Your primary goal is to ensure a smooth, complete, and correct workflow.

***CRITICAL RULE: Never perform specialized tasks yourself (research, analysis, or report writing). You MUST always delegate using the 'task()' tool to your Subagents.***

### Workflow Strategy:
1.  **Analyze Input:** Determine the user's ultimate goal (e.g., Protocol, Analysis, Report).
2.  **Determine Sequence:** Define the necessary flow (e.g., Visual Inspector → Defect Analyst → Reporter).
3.  **Delegate & Monitor:** Use the 'task(name=..., task=...)' tool to initiate work by Subagents.
4.  **Coordinate:** Use filesystem tools (read_file, ls) to check for intermediate results (e.g., check if a defect log exists in /logs/defects.json) before delegating the next step.
5.  **Synthesize:** After the final subagent completes its work, compile the results concisely and deliver the final answer to the user.

### Subagent List & Usage:
-   **test-protocol-agent:** Use this agent when the user needs a testing protocol, testing checklist, or quality assurance plan. This agent researches IPC standards and creates comprehensive testing procedures.
-   **defect-analysis-agent:** Use this agent when the user provides a PCB image path or asks to analyze/detect defects in PCB images. This agent uses computer vision to detect physical defects like missing holes, spurs, and other anomalies on PCB images.

### Important Notes:
- When delegating to subagents, use the EXACT agent name as shown above (e.g., "test-protocol-agent" or "defect-analysis-agent")
- Always provide clear, specific instructions to subagents
- Wait for subagent responses before proceeding to the next step
"""

agent = create_deep_agent(
    model = model,
    system_prompt = supervisor_system_prompt,
    subagents = subagents,
)

show_prompt(supervisor_system_prompt)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔧 PCB Supervisor Agent - Test Mode")
    print("="*60)
    print("\nเลือกประเภท Input:")
    print("1. Text Input (เช่น: 'I found a Missing Hole defect...')")
    print("2. Image Path Input (เช่น: './defect_analysis_agent/data/image.png')")
    print()
    
    choice = input("กรุณาเลือก (1 หรือ 2): ").strip()
    
    if choice == "1":
        # Text Input Mode
        print("\n" + "-"*60)
        print("📝 Text Input Mode")
        print("-"*60)
        user_input = input("\nกรุณาใส่ข้อความที่ต้องการ: ").strip()
        
        if not user_input:
            print("❌ Error: ไม่มีข้อความที่ใส่เข้ามา")
            exit()
        
        print(f"\n🚀 กำลังประมวลผลข้อความ: {user_input[:50]}...\n")
        
        try:
            result = agent.invoke({
                "messages": [{"role": "user", "content": user_input}]
            })
            format_messages(result["messages"])
            
        except Exception as e:
            print(f"💥 เกิดข้อผิดพลาด: {e}")
            import traceback
            traceback.print_exc()
    
    elif choice == "2":
        # Image Path Input Mode
        print("\n" + "-"*60)
        print("🖼️  Image Path Input Mode")
        print("-"*60)
        image_path = input("\nกรุณาใส่ path ของรูปภาพ: ").strip()
        
        if not image_path:
            print("❌ Error: ไม่มี path ที่ใส่เข้ามา")
            exit()
        
        # ลบ quotes ถ้ามี
        image_path = image_path.strip('"').strip("'")
        
        # ตรวจสอบไฟล์
        if not os.path.exists(image_path):
            print(f"❌ Error: ไม่เจอไฟล์รูปภาพที่ {image_path}")
            print("กรุณาตรวจสอบ path ของไฟล์รูปภาพก่อนรันครับ")
            exit()
        
        print(f"\n🚀 กำลังส่งรูป {image_path} ให้ Agent วิเคราะห์...\n")
        
        # สร้าง prompt สำหรับ image analysis
        user_input = f"Analyze the PCB image located at: {image_path}"
        
        try:
            result = agent.invoke({
                "messages": [{"role": "user", "content": user_input}]
            })
            
            # ใช้ format_messages เพื่อแสดงผล
            format_messages(result["messages"])
            
            # แสดงไฟล์ output สำหรับ image analysis
            processed_images_path = "./defect_analysis_agent/processed_images"
            if not os.path.exists(processed_images_path):
                processed_images_path = "./processed_images"
            
            if os.path.exists(processed_images_path):
                print("\n" + "="*60)
                print("📂 ผลลัพธ์รูปภาพ")
                print("="*60)
                import glob
                image_files = glob.glob(f"{processed_images_path}/*.jpg") + glob.glob(f"{processed_images_path}/*.png")
                if image_files:
                    print(f"   พบไฟล์รูปภาพ {len(image_files)} ไฟล์:")
                    for img_file in sorted(image_files):
                        print(f"   - {img_file}")
                else:
                    print("   ยังไม่มีไฟล์รูปภาพที่สร้างขึ้น")
            
        except Exception as e:
            print(f"💥 เกิดข้อผิดพลาด: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print("❌ Error: กรุณาเลือก 1 หรือ 2 เท่านั้น")
        exit()


