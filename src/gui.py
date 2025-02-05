import tkinter as tk
from tkinter import ttk, scrolledtext, Toplevel
import os
from .Agents.rag_agent import RAGAgent
from .Agents.technical_analysis_agent import TechnicalAnalysisAgent
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Initialize agents globally to maintain state
rag = RAGAgent()
rag.initialize_vector_store()
tech_agent = TechnicalAnalysisAgent()

class RAGGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Ransom's Alpha Box")
        self.root.geometry("1000x800")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.bg_color = "#E8F5E9"  # Light green background
        self.border_color = "#4CAF50"  # Green border
        self.title_color = "#2196F3"  # Blue title
        self.text_color = "#1B5E20"  # Dark green text
        
        # Configure root window
        self.root.configure(bg=self.border_color)
        
        # Create main frame with green border
        self.main_frame = tk.Frame(
            self.root,
            bg=self.border_color,
            padx=2,  # Border thickness
            pady=2   # Border thickness
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create inner frame with white background
        self.inner_frame = tk.Frame(
            self.main_frame,
            bg=self.bg_color
        )
        self.inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create title in blue
        title_label = ttk.Label(
            self.inner_frame,
            text="Ransom's Alpha Box",
            font=('Helvetica', 24, 'bold'),
            foreground=self.title_color,
            background=self.bg_color
        )
        title_label.pack(pady=(20, 20))
        
        # Create query frame
        query_frame = tk.Frame(self.inner_frame, bg=self.bg_color)
        query_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Create query entry
        self.query_entry = ttk.Entry(
            query_frame,
            font=('Helvetica', 12),
            width=50
        )
        self.query_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        # Create submit button
        submit_button = ttk.Button(
            query_frame,
            text="Submit Query",
            command=self.submit_query,
            style='Submit.TButton'
        )
        submit_button.pack(side=tk.RIGHT)
        
        # Create output frames
        outputs_frame = tk.Frame(self.inner_frame, bg=self.bg_color)
        outputs_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # RAG Agent output (left side)
        rag_frame = tk.Frame(outputs_frame, bg=self.border_color, padx=2, pady=2)
        rag_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        rag_label = ttk.Label(
            rag_frame,
            text="RAG Agent Output:",
            font=('Helvetica', 12, 'bold'),
            foreground=self.text_color,
            background=self.bg_color
        )
        rag_label.pack(anchor=tk.W, pady=5, padx=5)
        
        self.rag_output = scrolledtext.ScrolledText(
            rag_frame,
            wrap=tk.WORD,
            font=('Helvetica', 11),
            height=30,
            bg='white',
            fg=self.text_color
        )
        self.rag_output.pack(fill=tk.BOTH, expand=True)
        
        # Technical Analysis output (right side)
        tech_frame = tk.Frame(outputs_frame, bg=self.border_color, padx=2, pady=2)
        tech_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tech_label = ttk.Label(
            tech_frame,
            text="Technical Analysis Output:",
            font=('Helvetica', 12, 'bold'),
            foreground=self.text_color,
            background=self.bg_color
        )
        tech_label.pack(anchor=tk.W, pady=5, padx=5)
        
        self.tech_output = scrolledtext.ScrolledText(
            tech_frame,
            wrap=tk.WORD,
            font=('Helvetica', 11),
            height=30,
            bg='white',
            fg=self.text_color
        )
        self.tech_output.pack(fill=tk.BOTH, expand=True)
        
        # Configure custom styles
        style.configure(
            'Submit.TButton',
            background=self.border_color,
            foreground='white',
            padding=(20, 10)
        )
        
        # Bind enter key to submit
        self.query_entry.bind('<Return>', lambda e: self.submit_query())
        
        # Display welcome messages
        self.rag_output.insert(tk.END, "✓ RAG Agent ready.\n\nExample queries:\n1. Show me recent news for NVDA\n2. What are the fundamentals for AAPL?\n\nNote: Enter ticker without parentheses for RAG queries")
        self.tech_output.insert(tk.END, "✓ Technical Analysis Agent ready.\n\nExample query:\nTechnical analysis for (AAPL) last 30 days\n\nNote: Enter ticker in parentheses for Technical Analysis")

    def display_chart_popup(self, figure, title):
        """Display a matplotlib figure in a popup window"""
        popup = Toplevel(self.root)
        popup.title(title)
        popup.geometry("800x600")
        
        # Create canvas in popup
        canvas = FigureCanvasTkAgg(figure, master=popup)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def submit_query(self):
        """Handle query submission using RAG agent or Technical Analysis agent"""
        query = self.query_entry.get().strip()
        if not query:
            return
        
        try:
            # Check if query contains ticker in parentheses for technical analysis
            if '(' in query and ')' in query:
                self.tech_output.delete(1.0, tk.END)
                
                # Extract ticker for popup window title
                import re
                ticker_match = re.search(r'\(([^)]+)\)', query)
                ticker = ticker_match.group(1) if ticker_match else "Stock"
                
                # Use the technical analysis agent
                response, fig = tech_agent.analyze_ticker(query)
                self.tech_output.insert(tk.END, f"Query: {query}\n\n{response}")
                if fig:
                    self.display_chart_popup(fig, f"Technical Analysis Chart - {ticker}")
            else:
                self.rag_output.delete(1.0, tk.END)
                
                # Use the RAG agent for regular queries
                response = rag.generate_response(query)
                self.rag_output.insert(tk.END, f"Query: {query}\n\n{response}")
        except Exception as e:
            output = self.tech_output if '(' in query and ')' in query else self.rag_output
            output.insert(tk.END, f"❌ Error: {str(e)}\n")

def main():
    root = tk.Tk()
    app = RAGGui(root)
    root.mainloop()

if __name__ == "__main__":
    main()
