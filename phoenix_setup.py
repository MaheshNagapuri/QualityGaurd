"""
phoenix_setup.py
Run once before Streamlit to launch Phoenix dashboard.
"""
import phoenix as px
from openinference.instrumentation.crewai import CrewAIInstrumentor


def start_phoenix():
    # Phoenix launches and sets up its OWN TracerProvider internally
    session = px.launch_app()
    print(f"\n✅ Phoenix dashboard: {session.url}\n")

    # Instrument CrewAI using Phoenix's already-active tracer — no new provider needed
    CrewAIInstrumentor().instrument()

    print("CrewAI instrumentation active — all agent calls will be traced.")
    return session


if __name__ == "__main__":
    session = start_phoenix()
    print("Now start your app in another terminal:")
    print("  streamlit run main.py\n")
    input("Press Enter to stop Phoenix...")
