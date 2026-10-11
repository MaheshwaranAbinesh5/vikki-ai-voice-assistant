import json
 
import websockets
from dotenv import load_dotenv
 
from livekit import agents
from livekit.agents import AgentServer, AgentSession, Agent, RunContext, function_tool
from livekit.plugins import google
 
load_dotenv(".env")
 
# --- tiny bridge so robot.html can see what the assistant is doing ---
clients = set()
bridge_started = False
 
 s
async def _handler(ws):
    clients.add(ws)
    try:
        async for _ in ws:
            pass
    finally:
        clients.discard(ws)
 
 
def send_ui(msg: dict):
    websockets.broadcast(clients, json.dumps(msg))
 
 
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are Vikki, a helpful voice AI assistant.
            You eagerly assist users with their questions by providing information from your extensive knowledge.
            Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
            You are curious, friendly, and have a sense of humor.
            When the user says goodbye, bye, stop, quit, exit, or asks you to close, end, or shut down, say a short goodbye and call the end_conversation tool.""",
        )
 
    @function_tool
    async def end_conversation(self, context: RunContext):
        """Use this when the user wants to end the conversation or close the assistant,
        for example when they say bye, goodbye, stop, quit, exit, close, or shut down."""
        # drain=True lets the spoken goodbye finish before the session closes
        context.session.shutdown(drain=True)
        return "Say a very short goodbye to the user."
 
 
server = AgentServer()
 
 
@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: agents.JobContext):
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model="gemini-3.8-live",
            voice="Puck",
            temperature=0.8,
        ),
    )
 
    global bridge_started
    if not bridge_started:
        bridge_started = True
        await websockets.serve(_handler, "localhost", 8765)
 
    @session.on("agent_state_changed")
    def on_state(ev):
        send_ui({"type": "state", "state": ev.new_state})
 
    @session.on("conversation_item_added")
    def on_item(ev):
        text = getattr(ev.item, "text_content", None)
        role = getattr(ev.item, "role", None)
        if text and role:
            send_ui({"type": "text", "role": role, "text": text})
 
    @session.on("close")
    def on_close(_ev):
        ctx.shutdown(reason="user said goodbye")
 
    await session.start(
        room=ctx.room,
        agent=Assistant(),
    )
 
    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )
 
 
if __name__ == "__main__":
    agents.cli.run_app(server)
 







