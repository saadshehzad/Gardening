def add_llm(cursor):
    llms=[
            "ChatGPT",
            "DeepSeek"
        ]
    
    for llm in llms:
        try:
                cursor.execute("""
                    INSERT INTO plant_llm(name)
                    VALUES (%s);
                """, (llm,))
                
        except Exception as e:
                print(f"Error creating {llm}: {e}")
