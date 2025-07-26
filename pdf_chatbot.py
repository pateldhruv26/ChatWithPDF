from rag import get_pdf_content, get_conversation, get_response

def main():
    print("Welcome to PDF Chatbot")
    pdf_path = input("Enter the path to your PDF file: ").strip()

    print("\nReading and processing PDF...")
    text = get_pdf_content([pdf_path])
    
    print("Splitting and embedding content...")
    conversation = get_conversation(text)
    print("Ready! Ask me anything from the PDF. Type 'exit' to quit.\n")

    while True:
        question = input("You: ")
        if question.lower() in ["exit", "quit"]:
            print("Exiting chatbot. Goodbye!")
            break

        answer = get_response(conversation, question)
        print("Bot:", answer)
        print()

if __name__ == "__main__":
    main()
