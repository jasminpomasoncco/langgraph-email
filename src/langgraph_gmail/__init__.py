from langgraph_gmail.graph.email_graph import EmailSupportGraph


def main() -> None:
    print("Hello from langgraph-gmail!")
    initial_state = {
        "current_email": None,
        "email_category": "",
        "email_response": None,
        "messages": [],
    }
    workflow = EmailSupportGraph(initial_state=initial_state)
    graph = workflow.graph
    for output in graph.stream(initial_state):
        for node, state in output.items():
            print("Node:\n")
            print(f"{node}\n")
            print("State:\n")
            print(f"{state}\n")
            
    
if __name__ == "__main__":
    main()