#!/usr/bin/env python3
"""
Context GUI - A selection-based assistant with GUI and global hotkey support.
Press Ctrl+Shift+X to activate, then paste/enter text and configure options.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import threading
import pyperclip
import os
import sys
import time
from context import process_text, is_conversation, detect_language


class ContextGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Context Assistant")
        self.root.geometry("850x950")
        self.root.resizable(True, True)
        
        # Set minimum window size
        self.root.minsize(750, 800)
        
        # Professional color scheme
        self.colors = {
            'bg': '#1a1a1a',  # Deep dark background
            'fg': '#f5f5f5',  # Soft white text
            'accent': '#0066cc',  # Professional blue
            'accent_hover': '#0052a3',
            'accent_light': '#e6f2ff',  # Light accent for hover
            'secondary': '#252525',  # Secondary background
            'secondary_hover': '#2d2d2d',
            'border': '#333333',  # Subtle borders
            'border_light': '#404040',
            'text_area_bg': '#0f0f0f',  # Very dark for text areas
            'text_area_fg': '#e8e8e8',
            'text_area_border': '#2a2a2a',
            'success': '#28a745',
            'success_hover': '#218838',
            'warning': '#ffc107',
            'error': '#dc3545',
            'card_bg': '#212121',  # Card background
            'divider': '#2d2d2d'  # Divider lines
        }
        
        # Configure root background
        self.root.configure(bg=self.colors['bg'])
        
        # Try to get API key from environment
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        
        # Animation state
        self.animation_running = False
        self.loading_dots = 0
        self.loading_animation_id = None
        
        # Setup styles
        self.setup_styles()
        
        # Setup UI
        self.setup_ui()
        
        # Animate window appearance
        self.animate_window_fade_in()
        
        # Auto-paste from clipboard on startup
        self.root.after(300, self.paste_from_clipboard)
        
        # Focus on text input
        self.root.after(500, lambda: self.text_input.focus())
    
    def setup_styles(self):
        """Setup modern ttk styles."""
        style = ttk.Style()
        
        # Try to use a modern theme
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Configure styles
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 18, 'bold'),
                       background=self.colors['bg'],
                       foreground=self.colors['accent'])
        
        style.configure('Heading.TLabel',
                       font=('Segoe UI', 11, 'bold'),
                       background=self.colors['bg'],
                       foreground=self.colors['fg'])
        
        style.configure('Section.TLabelFrame',
                       background=self.colors['bg'],
                       foreground=self.colors['fg'],
                       borderwidth=1,
                       relief='flat')
        
        style.configure('Section.TLabelFrame.Label',
                       background=self.colors['bg'],
                       foreground=self.colors['accent'],
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('Primary.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       padding=(20, 10))
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['accent_hover']),
                            ('!active', self.colors['accent'])],
                 foreground=[('active', '#ffffff'),
                            ('!active', '#ffffff')])
        
        style.configure('Secondary.TButton',
                       font=('Segoe UI', 9),
                       padding=(10, 5))
        
        style.configure('Modern.TEntry',
                       fieldbackground=self.colors['text_area_bg'],
                       foreground=self.colors['text_area_fg'],
                       borderwidth=1,
                       relief='solid',
                       padding=5)
        
        style.configure('Modern.TCombobox',
                       fieldbackground=self.colors['text_area_bg'],
                       foreground=self.colors['text_area_fg'],
                       borderwidth=1,
                       padding=5,
                       relief='flat')
        
        style.map('Modern.TCombobox',
                 fieldbackground=[('readonly', self.colors['text_area_bg'])],
                 selectbackground=[('readonly', self.colors['accent'])],
                 selectforeground=[('readonly', '#ffffff')])
        
        style.configure('Status.TLabel',
                       font=('Segoe UI', 9),
                       background=self.colors['secondary'],
                       foreground=self.colors['fg'],
                       padding=(10, 5),
                       relief='flat')
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main container with professional padding
        main_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=24, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Professional header section
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 24))
        
        title_label = tk.Label(header_frame, 
                               text="Context Assistant",
                               font=('Segoe UI', 28, 'bold'),
                               bg=self.colors['bg'],
                               fg=self.colors['fg'])
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(header_frame,
                                  text="AI-powered text processing • Press Ctrl+Shift+X to activate",
                                  font=('Segoe UI', 10),
                                  bg=self.colors['bg'],
                                  fg='#999999')
        subtitle_label.pack(anchor=tk.W, pady=(6, 0))
        
        # API Key section - Professional card design
        api_card = tk.Frame(main_frame, bg=self.colors['card_bg'], relief=tk.FLAT)
        api_card.pack(fill=tk.X, pady=(0, 18))
        
        # Card border effect
        border_frame = tk.Frame(api_card, bg=self.colors['border'], height=1)
        border_frame.pack(fill=tk.X)
        
        api_inner = tk.Frame(api_card, bg=self.colors['card_bg'], padx=18, pady=16)
        api_inner.pack(fill=tk.X)
        
        api_label = tk.Label(api_inner, text="API Key", 
                             font=('Segoe UI', 11, 'bold'),
                             bg=self.colors['card_bg'],
                             fg=self.colors['fg'])
        api_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 12))
        
        self.api_key_var = tk.StringVar(value=self.api_key)
        api_entry = tk.Entry(api_inner, textvariable=self.api_key_var, show="•",
                            font=('Segoe UI', 10),
                            bg=self.colors['text_area_bg'],
                            fg=self.colors['text_area_fg'],
                            insertbackground=self.colors['accent'],
                            relief=tk.FLAT,
                            bd=1,
                            highlightthickness=1,
                            highlightbackground=self.colors['border'],
                            highlightcolor=self.colors['accent'],
                            width=50)
        api_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 12), ipady=8)
        api_inner.columnconfigure(1, weight=1)
        
        save_btn = tk.Button(api_inner, text="Save", 
                            command=self.save_api_key,
                            font=('Segoe UI', 10, 'bold'),
                            bg=self.colors['accent'],
                            fg='#ffffff',
                            activebackground=self.colors['accent_hover'],
                            activeforeground='#ffffff',
                            relief=tk.FLAT,
                            padx=24,
                            pady=8,
                            cursor='hand2',
                            bd=0)
        save_btn.grid(row=0, column=2)
        
        # Text input section - Professional card
        text_section = tk.Frame(main_frame, bg=self.colors['bg'])
        text_section.pack(fill=tk.BOTH, expand=True, pady=(0, 18))
        
        text_header_frame = tk.Frame(text_section, bg=self.colors['bg'])
        text_header_frame.pack(fill=tk.X, pady=(0, 10))
        
        text_header = tk.Label(text_header_frame,
                               text="Input Text",
                               font=('Segoe UI', 13, 'bold'),
                               bg=self.colors['bg'],
                               fg=self.colors['fg'])
        text_header.pack(side=tk.LEFT)
        
        paste_btn = tk.Button(text_header_frame,
                             text="Paste from Clipboard",
                             command=self.paste_from_clipboard,
                             font=('Segoe UI', 9),
                             bg=self.colors['secondary'],
                             fg=self.colors['fg'],
                             activebackground=self.colors['secondary_hover'],
                             activeforeground=self.colors['fg'],
                             relief=tk.FLAT,
                             padx=16,
                             pady=6,
                             cursor='hand2',
                             bd=0)
        paste_btn.pack(side=tk.RIGHT)
        
        text_card = tk.Frame(text_section, bg=self.colors['card_bg'], relief=tk.FLAT)
        text_card.pack(fill=tk.BOTH, expand=True)
        
        # Card border
        border_frame = tk.Frame(text_card, bg=self.colors['border'], height=1)
        border_frame.pack(fill=tk.X)
        
        text_container = tk.Frame(text_card, bg=self.colors['text_area_bg'], relief=tk.FLAT)
        text_container.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.text_input = scrolledtext.ScrolledText(text_container,
                                                    height=11,
                                                    wrap=tk.WORD,
                                                    font=('Segoe UI', 10),
                                                    bg=self.colors['text_area_bg'],
                                                    fg=self.colors['text_area_fg'],
                                                    insertbackground=self.colors['accent'],
                                                    relief=tk.FLAT,
                                                    padx=16,
                                                    pady=16,
                                                    bd=0,
                                                    highlightthickness=0)
        self.text_input.pack(fill=tk.BOTH, expand=True)
        
        # Options section - Professional card
        options_card = tk.Frame(main_frame, bg=self.colors['card_bg'], relief=tk.FLAT)
        options_card.pack(fill=tk.X, pady=(0, 18))
        
        # Card border
        border_frame = tk.Frame(options_card, bg=self.colors['border'], height=1)
        border_frame.pack(fill=tk.X)
        
        options_inner = tk.Frame(options_card, bg=self.colors['card_bg'], padx=18, pady=18)
        options_inner.pack(fill=tk.X)
        
        options_title = tk.Label(options_inner,
                                text="Processing Options",
                                font=('Segoe UI', 12, 'bold'),
                                bg=self.colors['card_bg'],
                                fg=self.colors['fg'])
        options_title.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 14))
        
        # Intent/Instruction
        intent_label = tk.Label(options_inner,
                               text="Intent / Instruction",
                               font=('Segoe UI', 10),
                               bg=self.colors['card_bg'],
                               fg='#cccccc')
        intent_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 6), padx=(0, 12))
        
        self.intent_var = tk.StringVar()
        intent_entry = tk.Entry(options_inner,
                               textvariable=self.intent_var,
                               font=('Segoe UI', 10),
                               bg=self.colors['text_area_bg'],
                               fg=self.colors['text_area_fg'],
                               insertbackground=self.colors['accent'],
                               relief=tk.FLAT,
                               bd=1,
                               highlightthickness=1,
                               highlightbackground=self.colors['border'],
                               highlightcolor=self.colors['accent'],
                               width=42)
        intent_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 6), ipady=8)
        
        # Divider
        divider1 = tk.Frame(options_inner, bg=self.colors['divider'], height=1)
        divider1.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Style
        style_label = tk.Label(options_inner,
                              text="Style",
                              font=('Segoe UI', 10),
                              bg=self.colors['card_bg'],
                              fg='#cccccc')
        style_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 6), padx=(0, 12))
        
        self.style_var = tk.StringVar()
        style_combo = ttk.Combobox(options_inner,
                                  textvariable=self.style_var,
                                  values=('', 'formal', 'casual', 'professional', 'friendly', 'technical', 'simple', 'detailed'),
                                  font=('Segoe UI', 10),
                                  state='readonly',
                                  width=39,
                                  style='Modern.TCombobox')
        style_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(0, 6))
        
        # Divider
        divider2 = tk.Frame(options_inner, bg=self.colors['divider'], height=1)
        divider2.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Length
        length_label = tk.Label(options_inner,
                               text="Length",
                               font=('Segoe UI', 10),
                               bg=self.colors['card_bg'],
                               fg='#cccccc')
        length_label.grid(row=5, column=0, sticky=tk.W, pady=(0, 6), padx=(0, 12))
        
        self.length_var = tk.StringVar()
        length_combo = ttk.Combobox(options_inner,
                                    textvariable=self.length_var,
                                    values=('', 'short', 'medium', 'long'),
                                    font=('Segoe UI', 10),
                                    state='readonly',
                                    width=39,
                                    style='Modern.TCombobox')
        length_combo.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=(0, 6))
        
        options_inner.columnconfigure(1, weight=1)
        
        # Process button - Professional primary action
        process_btn = tk.Button(main_frame,
                               text="Process & Copy to Clipboard",
                               command=self.process_and_copy,
                               font=('Segoe UI', 11, 'bold'),
                               bg=self.colors['accent'],
                               fg='#ffffff',
                               activebackground=self.colors['accent_hover'],
                               activeforeground='#ffffff',
                               relief=tk.FLAT,
                               padx=0,
                               pady=14,
                               cursor='hand2',
                               bd=0)
        process_btn.pack(fill=tk.X, pady=(0, 18))
        
        # Result section - Professional card
        result_section = tk.Frame(main_frame, bg=self.colors['bg'])
        result_section.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        result_header = tk.Label(result_section,
                                text="Result",
                                font=('Segoe UI', 13, 'bold'),
                                bg=self.colors['bg'],
                                fg=self.colors['fg'])
        result_header.pack(anchor=tk.W, pady=(0, 10))
        
        result_card = tk.Frame(result_section, bg=self.colors['card_bg'], relief=tk.FLAT)
        result_card.pack(fill=tk.BOTH, expand=True)
        
        # Card border
        border_frame = tk.Frame(result_card, bg=self.colors['border'], height=1)
        border_frame.pack(fill=tk.X)
        
        result_container = tk.Frame(result_card, bg=self.colors['text_area_bg'], relief=tk.FLAT)
        result_container.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.result_text = scrolledtext.ScrolledText(result_container,
                                                      height=9,
                                                      wrap=tk.WORD,
                                                      font=('Segoe UI', 10),
                                                      bg=self.colors['text_area_bg'],
                                                      fg=self.colors['text_area_fg'],
                                                      state=tk.DISABLED,
                                                      relief=tk.FLAT,
                                                      padx=16,
                                                      pady=16,
                                                      bd=0,
                                                      highlightthickness=0)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar - Professional footer
        status_frame = tk.Frame(main_frame, bg=self.colors['card_bg'], relief=tk.FLAT)
        status_frame.pack(fill=tk.X, pady=(12, 0))
        
        # Top border
        border_frame = tk.Frame(status_frame, bg=self.colors['border'], height=1)
        border_frame.pack(fill=tk.X)
        
        self.status_var = tk.StringVar(value="Ready. Press Ctrl+Shift+X to activate from anywhere.")
        self.status_bar = tk.Label(status_frame,
                            textvariable=self.status_var,
                            font=('Segoe UI', 9),
                            bg=self.colors['card_bg'],
                            fg='#999999',
                            anchor=tk.W,
                            padx=18,
                            pady=12)
        self.status_bar.pack(fill=tk.X)
        
        # Store button references for animations
        self.process_btn = process_btn
        self.paste_btn = paste_btn
        self.save_btn = save_btn
        
        # Add hover animations to buttons
        self.setup_button_animations()
    
    def animate_window_fade_in(self):
        """Animate window fade-in effect."""
        try:
            # Start with low opacity (if supported)
            self.root.attributes('-alpha', 0.0)
            
            def fade_in(alpha=0.0):
                if alpha < 1.0:
                    alpha += 0.1
                    try:
                        self.root.attributes('-alpha', alpha)
                    except:
                        pass  # Alpha not supported on all systems
                    self.root.after(20, lambda: fade_in(alpha))
                else:
                    try:
                        self.root.attributes('-alpha', 1.0)
                    except:
                        pass
            
            fade_in()
        except:
            pass  # Alpha transparency not supported
    
    def setup_button_animations(self):
        """Setup hover and click animations for buttons."""
        # Process button animations
        def on_process_enter(e):
            self.animate_button_scale(self.process_btn, 1.02)
        
        def on_process_leave(e):
            self.animate_button_scale(self.process_btn, 1.0)
        
        self.process_btn.bind('<Enter>', on_process_enter)
        self.process_btn.bind('<Leave>', on_process_leave)
        
        # Paste button animations
        def on_paste_enter(e):
            self.paste_btn.config(bg=self.colors['secondary_hover'])
        
        def on_paste_leave(e):
            self.paste_btn.config(bg=self.colors['secondary'])
        
        self.paste_btn.bind('<Enter>', on_paste_enter)
        self.paste_btn.bind('<Leave>', on_paste_leave)
        
        # Save button animations
        def on_save_enter(e):
            self.save_btn.config(bg=self.colors['accent_hover'])
        
        def on_save_leave(e):
            self.save_btn.config(bg=self.colors['accent'])
        
        self.save_btn.bind('<Enter>', on_save_enter)
        self.save_btn.bind('<Leave>', on_save_leave)
    
    def animate_button_scale(self, button, target_scale):
        """Animate button scale effect using padding instead of font size."""
        # Store original padding
        if not hasattr(button, '_original_padx'):
            button._original_padx = button.cget('padx')
            button._original_pady = button.cget('pady')
        
        original_padx = button._original_padx if isinstance(button._original_padx, (int, tuple)) else (button._original_padx, button._original_padx) if isinstance(button._original_padx, int) else (30, 30)
        original_pady = button._original_pady if isinstance(button._original_pady, (int, tuple)) else (button._original_pady, button._original_pady) if isinstance(button._original_pady, int) else (15, 15)
        
        # Convert to tuple if single value
        if isinstance(original_padx, int):
            original_padx = (original_padx, original_padx)
        if isinstance(original_pady, int):
            original_pady = (original_pady, original_pady)
        
        base_padx = original_padx[0] if isinstance(original_padx, tuple) else original_padx
        base_pady = original_pady[0] if isinstance(original_pady, tuple) else original_pady
        
        def scale_step(current, target, step=0.02):
            if abs(current - target) > step:
                new_padx = int(base_padx * current)
                new_pady = int(base_pady * current)
                try:
                    button.config(padx=new_padx, pady=new_pady)
                except:
                    pass
                if current < target:
                    self.root.after(15, lambda: scale_step(min(current + step, target), target, step))
                else:
                    self.root.after(15, lambda: scale_step(max(current - step, target), target, step))
            else:
                final_padx = int(base_padx * target)
                final_pady = int(base_pady * target)
                try:
                    button.config(padx=final_padx, pady=final_pady)
                except:
                    pass
        
        # Get current scale (approximate)
        current_scale = 1.0
        scale_step(current_scale, target_scale)
    
    def animate_button_brightness(self, button, brightness):
        """Animate button brightness change with professional hover effect."""
        original_bg = button.cget('bg')
        
        # For secondary buttons, use hover color directly
        if original_bg == self.colors['secondary']:
            button.config(bg=self.colors['secondary_hover'])
        else:
            def hex_to_rgb(hex_color):
                hex_color = hex_color.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            def rgb_to_hex(rgb):
                return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
            
            def brighten_color(hex_color, factor):
                rgb = hex_to_rgb(hex_color)
                new_rgb = tuple(min(255, int(c * factor)) for c in rgb)
                return rgb_to_hex(new_rgb)
            
            try:
                new_bg = brighten_color(original_bg, brightness)
                button.config(bg=new_bg)
            except:
                pass
    
    def animate_loading_status(self):
        """Animate loading dots in status bar."""
        if self.animation_running:
            dots = '.' * (self.loading_dots % 4)
            self.status_var.set(f"Processing{dots}")
            self.loading_dots += 1
            self.loading_animation_id = self.root.after(300, self.animate_loading_status)
    
    def stop_loading_animation(self):
        """Stop the loading animation."""
        self.animation_running = False
        if self.loading_animation_id:
            self.root.after_cancel(self.loading_animation_id)
            self.loading_animation_id = None
    
    def animate_text_fade_in(self, widget, text, delay=0):
        """Animate text fade-in effect."""
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        
        # For long text, use chunk-based animation for better performance
        if len(text) > 500:
            chunk_size = 20
            def insert_chunks(text, start=0):
                if start < len(text):
                    end = min(start + chunk_size, len(text))
                    widget.insert(tk.END, text[start:end])
                    widget.see(tk.END)
                    self.root.after(10, lambda: insert_chunks(text, end))
                else:
                    widget.config(state=tk.DISABLED)
            self.root.after(delay, lambda: insert_chunks(text))
        else:
            # For shorter text, use character-by-character for smoother effect
            def insert_char_by_char(text, index=0):
                if index < len(text):
                    widget.insert(tk.END, text[index])
                    widget.see(tk.END)
                    self.root.after(2, lambda: insert_char_by_char(text, index + 1))
                else:
                    widget.config(state=tk.DISABLED)
            self.root.after(delay, lambda: insert_char_by_char(text))
        
    def paste_from_clipboard(self):
        """Paste text from clipboard into the text input."""
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text:
                # Animate text appearance
                self.text_input.delete(1.0, tk.END)
                self.animate_text_fade_in(self.text_input, clipboard_text)
                self.animate_status_update("Text pasted from clipboard", self.colors['success'])
        except Exception as e:
            self.animate_status_update(f"Error reading clipboard: {e}", self.colors['error'])
    
    def animate_status_update(self, message, color=None):
        """Animate status bar update with color transition."""
        def update():
            self.status_var.set(message)
            if color and hasattr(self, 'status_bar'):
                try:
                    self.status_bar.config(fg=color)
                    # Fade back to normal color
                    self.root.after(2000, lambda: self.status_bar.config(fg=self.colors['fg']))
                except:
                    pass
        
        update()
    
    def save_api_key(self):
        """Save API key."""
        self.api_key = self.api_key_var.get().strip()
        if self.api_key:
            os.environ['OPENAI_API_KEY'] = self.api_key
            self.animate_status_update("API key saved successfully", self.colors['success'])
            # Button click animation
            self.animate_button_click(self.save_btn)
        else:
            self.animate_status_update("API key cleared", self.colors['warning'])
    
    def animate_button_click(self, button):
        """Animate button click effect."""
        original_bg = button.cget('bg')
        
        def flash():
            try:
                button.config(bg=self.colors['accent_hover'])
                self.root.after(100, lambda: button.config(bg=original_bg))
            except:
                pass
        
        flash()
    
    def process_and_copy(self):
        """Process the text and copy result to clipboard."""
        text = self.text_input.get(1.0, tk.END).strip()
        
        if not text:
            messagebox.showwarning("No Text", "Please enter or paste some text to process.")
            return
        
        if not self.api_key:
            self.api_key = os.getenv('OPENAI_API_KEY', '')
        
        if not self.api_key:
            messagebox.showerror("API Key Required", 
                               "Please enter your OpenAI API key in the API Key field.")
            return
        
        # Get options
        intent = self.intent_var.get().strip() or None
        style = self.style_var.get().strip() or None
        length = self.length_var.get().strip() or None
        
        # Start loading animation
        self.animation_running = True
        self.loading_dots = 0
        self.animate_loading_status()
        
        # Disable process button during processing
        self.process_btn.config(state=tk.DISABLED, text="Processing...")
        
        # Process in a separate thread to avoid freezing UI
        def process_thread():
            try:
                result = process_text(
                    text, 
                    intent=intent, 
                    style=style, 
                    length=length,
                    use_llm=True,
                    api_key=self.api_key
                )
                
                # Update UI in main thread
                self.root.after(0, lambda: self.display_result(result))
            except Exception as e:
                self.root.after(0, lambda: self.display_error(str(e)))
        
        threading.Thread(target=process_thread, daemon=True).start()
    
    def display_result(self, result):
        """Display the result and copy to clipboard."""
        # Stop loading animation
        self.stop_loading_animation()
        
        # Re-enable process button
        self.process_btn.config(state=tk.NORMAL, text="Process & Copy to Clipboard")
        
        # Animate result text appearance
        self.animate_text_fade_in(self.result_text, result)
        
        # Copy to clipboard
        try:
            pyperclip.copy(result)
            self.animate_status_update("Result processed and copied to clipboard!", self.colors['success'])
            # Success animation on button
            self.animate_success_flash()
        except Exception as e:
            self.animate_status_update(f"Result processed but clipboard error: {e}", self.colors['warning'])
    
    def animate_success_flash(self):
        """Animate success flash on process button."""
        original_bg = self.process_btn.cget('bg')
        original_text = self.process_btn.cget('text')
        
        def flash_sequence(count=0):
            if count < 3:
                if count % 2 == 0:
                    self.process_btn.config(bg=self.colors['success'], text="Copied!")
                else:
                    self.process_btn.config(bg=original_bg, text=original_text)
                self.root.after(200, lambda: flash_sequence(count + 1))
            else:
                self.process_btn.config(bg=original_bg, text=original_text)
        
        flash_sequence()
    
    def display_error(self, error_msg):
        """Display an error message."""
        # Stop loading animation
        self.stop_loading_animation()
        
        # Re-enable process button
        self.process_btn.config(state=tk.NORMAL, text="Process & Copy to Clipboard")
        
        # Animate error display
        error_text = f"Error: {error_msg}"
        self.animate_text_fade_in(self.result_text, error_text)
        self.animate_status_update(f"Error: {error_msg}", self.colors['error'])
        
        # Error flash on button
        original_bg = self.process_btn.cget('bg')
        self.process_btn.config(bg=self.colors['error'])
        self.root.after(1000, lambda: self.process_btn.config(bg=original_bg))


class GlobalHotkeyListener:
    """Handles global hotkey listening and window activation."""
    
    def __init__(self, root):
        self.root = root
        self.app = None
        self.listening = False
        self.hotkey_thread = None
        
    def start_listening(self):
        """Start listening for global hotkey (Ctrl+Shift+X)."""
        try:
            import keyboard
            
            def on_hotkey():
                """Called when hotkey is pressed."""
                # Bring window to front
                self.root.after(0, self.activate_window)
            
            # Register global hotkey
            keyboard.add_hotkey('ctrl+shift+x', on_hotkey)
            self.listening = True
            print("Global hotkey registered: Ctrl+Shift+X")
            print("Press Ctrl+Shift+X from anywhere to activate Context Assistant")
        except ImportError:
            print("Warning: 'keyboard' package not installed.")
            print("Global hotkey support disabled. Install with: pip install keyboard")
            print("You can still run the GUI directly.")
        except Exception as e:
            print(f"Error setting up hotkey: {e}")
    
    def activate_window(self):
        """Activate and bring window to front with animation."""
        self.root.deiconify()  # Show window if minimized
        
        # Get screen dimensions for slide animation
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Get window dimensions
        self.root.update_idletasks()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # Calculate center position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Start from right side of screen
        start_x = screen_width
        self.root.geometry(f"{window_width}x{window_height}+{start_x}+{y}")
        
        # Animate slide-in
        def slide_in(current_x, target_x, step=20):
            if current_x > target_x:
                new_x = max(current_x - step, target_x)
                self.root.geometry(f"{window_width}x{window_height}+{new_x}+{y}")
                if new_x > target_x:
                    self.root.after(10, lambda: slide_in(new_x, target_x, step))
                else:
                    # Animation complete
                    self.root.lift()
                    self.root.focus_force()
                    try:
                        self.root.attributes('-topmost', True)
                        self.root.after(100, lambda: self.root.attributes('-topmost', False))
                    except:
                        pass
                    # Auto-paste from clipboard when activated
                    if self.app:
                        self.root.after(100, self.app.paste_from_clipboard)
            else:
                self.root.lift()
                self.root.focus_force()
        
        slide_in(start_x, x)


def main():
    """Main entry point."""
    root = tk.Tk()
    app = ContextGUI(root)
    
    # Setup global hotkey listener
    hotkey_listener = GlobalHotkeyListener(root)
    hotkey_listener.start_listening()
    
    # Handle window close - minimize instead of closing
    def on_closing():
        root.withdraw()  # Hide window instead of closing
        app.status_var.set("Minimized. Press Ctrl+Shift+X to show again.")
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Make app accessible to hotkey listener
    hotkey_listener.app = app
    
    # Start GUI
    root.mainloop()


if __name__ == '__main__':
    main()

