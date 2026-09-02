from langgraph_gmail.graph.email_graph import EmailSupportGraph
from langgraph_gmail.state import Email


def main() -> None:
    print("Hello from langgraph-gmail!")
    initial_state = {
        "current_email": {
            "id": "",
            "subject": "",
            "sender": "",
            "body": "",
            "date": ""
        },
        "email_category": ""
    }
    workflow = EmailSupportGraph(initial_state=initial_state)
    graph = workflow.graph
    final_state = graph.invoke(initial_state)
    current_email = final_state.get("current_email")
    if isinstance(current_email, Email):
        print(current_email.body)
        print("Email Category:", final_state.get("email_category", ""))
    
if __name__ == "__main__":
    main()