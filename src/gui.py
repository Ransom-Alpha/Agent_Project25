import tkinter as tk
from tkinter import ttk, scrolledtext
import os
from Agents.rag_agent import RAGAgent

class RAGGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Ransom's Alpha Box")
        self.root.geometry("800x600")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme for modern look
        
        # Configure colors
        self.bg_color = "#f0f0f0"
        self.accent_color = "#2c3e50"
        self.text_color = "#2c3e50"
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Create main frame with border
        self.main_frame = ttk.Frame(self.root, padding="10", style='Card.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create title with decorative line
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="Ransom's Alpha Box",
            font=('Helvetica', 24, 'bold'),
            foreground=self.accent_color
        )
        title_label.pack(pady=(0, 5))
        
        separator = ttk.Separator(title_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 10))
        
        # Create query frame
        query_frame = ttk.Frame(self.main_frame)
        query_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create query label
        query_label = ttk.Label(
            query_frame,
            text="Enter your query:",
            font=('Helvetica', 12),
            foreground=self.text_color
        )
        query_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Create query entry with search icon
        self.query_entry = ttk.Entry(
            query_frame,
            font=('Helvetica', 12),
            width=50
        )
        self.query_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        # Create submit button
        submit_button = ttk.Button(
            query_frame,
            text="Search",
            command=self.submit_query,
            style='Accent.TButton'
        )
        submit_button.pack(side=tk.RIGHT)
        
        # Create results area with border
        results_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Results label
        results_label = ttk.Label(
            results_frame,
            text="Results:",
            font=('Helvetica', 12),
            foreground=self.text_color
        )
        results_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.results_area = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=('Helvetica', 11),
            height=20,
            bg='white',
            fg=self.text_color,
            padx=10,
            pady=10
        )
        self.results_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Initialize RAG Agent
        try:
            self.rag_agent = RAGAgent()
            self.rag_agent.initialize_vector_store()
            self.results_area.insert(tk.END, "✓ System ready. Please enter your query.\n\n")
            self.results_area.insert(tk.END, "Example queries:\n")
            self.results_area.insert(tk.END, "1. What was the lowest price for META in the last 10 days?\n")
            self.results_area.insert(tk.END, "2. Show me recent news for NVDA\n")
            self.results_area.insert(tk.END, "3. What are the fundamentals for AAPL?\n")
        except Exception as e:
            self.results_area.insert(tk.END, f"❌ Error initializing RAG agent: {str(e)}\n")
        
        # Bind enter key to submit
        self.query_entry.bind('<Return>', lambda e: self.submit_query())
        
        # Configure custom styles
        style.configure(
            'Accent.TButton',
            background=self.accent_color,
            foreground='white',
            padding=(20, 10)
        )
        
        style.configure(
            'Card.TFrame',
            background='white',
            relief='solid',
            borderwidth=1
        )

    def submit_query(self):
        """Handle query submission using RAG agent"""
        query = self.query_entry.get().strip()
        if not query:
            return
            
        self.results_area.delete(1.0, tk.END)
        self.results_area.insert(tk.END, f"Query: {query}\n\n")
        
        try:
            response = self.rag_agent.generate_response(query)
            self.results_area.insert(tk.END, response)
        except Exception as e:
            self.results_area.insert(tk.END, f"❌ Error: {str(e)}\n")

def main():
    root = tk.Tk()
    app = RAGGui(root)
    root.mainloop()

if __name__ == "__main__":
    main()
