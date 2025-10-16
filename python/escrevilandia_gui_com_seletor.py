import tkinter as tk
from tkinter import messagebox, filedialog
import tkinter.font as tkFont
import random
import string
from collections import Counter
import math # Para math.ceil

# Classe para a nova tela de avaliação individual
class AvaliacaoScreen:
    def __init__(self, master, palavras_icones):
        self.master = master
        self.palavras_icones = palavras_icones
        self.current_word_index = 0
        self.child_input_history = [] # Para armazenar o que a criança digitou em cada palavra
        self.analysis_results_history = [] # Para armazenar os resultados da análise detalhada e scores

        self.setup_ui()
        self.display_current_word()

    def setup_ui(self):
        self.avaliacao_window = tk.Toplevel(self.master)
        self.avaliacao_window.title("Escrevilândia: Avaliação da Escrita")
        self.avaliacao_window.geometry("400x750") # Tamanho ajustado para a nova tela
        self.avaliacao_window.resizable(True, True)
        self.avaliacao_window.transient(self.master)
        self.avaliacao_window.grab_set()
        self.avaliacao_window.focus_set()
        self.avaliacao_window.protocol("WM_DELETE_WINDOW", self.on_closing) # Lidar com o fechamento da janela

        # Configurar o grid da janela de avaliação
        self.avaliacao_window.grid_rowconfigure(0, weight=0) # Ícone
        self.avaliacao_window.grid_rowconfigure(1, weight=0) # Progresso
        self.avaliacao_window.grid_rowconfigure(2, weight=0) # Campo de digitação
        self.avaliacao_window.grid_rowconfigure(3, weight=1) # Banco de letras (expansível)
        self.avaliacao_window.grid_rowconfigure(4, weight=1) # Área de análise (expansível)
        self.avaliacao_window.grid_rowconfigure(5, weight=0) # Botões de navegação
        self.avaliacao_window.grid_columnconfigure(0, weight=1)

        # Frame principal para o conteúdo rolável (se necessário no futuro, mas por enquanto, direto)
        main_frame = tk.Frame(self.avaliacao_window, bg="#F0F2F5", padx=15, pady=15)
        main_frame.grid(row=0, column=0, sticky="nsew", rowspan=6) # Ocupa todas as linhas e colunas
        main_frame.grid_rowconfigure(3, weight=1) # Banco de letras
        main_frame.grid_rowconfigure(4, weight=1) # Área de análise
        main_frame.grid_columnconfigure(0, weight=1)

        # --- Ícone Centralizado ---
        self.icon_label = tk.Label(main_frame, text="", font=("Segoe UI Emoji", 60), bg="#F0F2F5", pady=10)
        self.icon_label.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        # --- Nível de Progresso ---
        self.progress_label = tk.Label(main_frame, text="", font=tkFont.Font(family="Arial", size=12), bg="#F0F2F5", fg="#666666")
        self.progress_label.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # --- Campo para digitação das letras ---
        input_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid", padx=10, pady=10)
        input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 15))
        input_frame.grid_columnconfigure(0, weight=1)

        tk.Label(input_frame, text="Escreva aqui:", font=tkFont.Font(family="Arial", size=11, weight="bold"), bg="white").pack(anchor="w")
        self.child_entry_var = tk.StringVar()
        self.child_entry = tk.Entry(input_frame, textvariable=self.child_entry_var, font=tkFont.Font(family="Arial", size=18), bd=0, relief="flat", bg="white", justify="center")
        self.child_entry.pack(fill="x", pady=5)
        self.child_entry.bind("<KeyRelease>", self.validate_input) # Validação ao digitar

        # --- Banco de Letras (Botões) ---
        self.letter_bank_frame = tk.Frame(main_frame, bg="#F0F2F5", padx=10, pady=10, bd=1, relief="solid")
        self.letter_bank_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 15))
        self.letter_bank_frame.grid_columnconfigure(0, weight=1) # Para centralizar o conteúdo

        self.letter_buttons_container = tk.Frame(self.letter_bank_frame, bg="#F0F2F5")
        self.letter_buttons_container.pack(expand=True) # Para centralizar os botões horizontalmente

        # --- Área de Análise ---
        analysis_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid", padx=10, pady=10)
        analysis_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 15))
        analysis_frame.grid_columnconfigure(0, weight=1)
        analysis_frame.grid_rowconfigure(0, weight=1)

        tk.Label(analysis_frame, text="Análise da Hipótese:", font=tkFont.Font(family="Arial", size=12, weight="bold"), bg="white", anchor="w").pack(fill="x")
        self.analysis_text = tk.Text(analysis_frame, font=tkFont.Font(family="Arial", size=10), bg="#F9F9F9", wrap="word", height=8, bd=0, relief="flat")
        self.analysis_text.pack(fill="both", expand=True, pady=(5,0))
        self.analysis_text.config(state="disabled") # Somente leitura

        # --- Botões de Navegação ---
        nav_buttons_frame = tk.Frame(main_frame, bg="#F0F2F5", pady=10)
        nav_buttons_frame.grid(row=5, column=0, sticky="ew")
        nav_buttons_frame.grid_columnconfigure(0, weight=1)
        nav_buttons_frame.grid_columnconfigure(1, weight=1)

        self.prev_button = tk.Button(nav_buttons_frame, text="Anterior", command=self.prev_word,
                                     font=tkFont.Font(family="Arial", size=10), bg="#FFC107", fg="white",
                                     padx=15, pady=8, relief="raised", bd=2)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.next_button = tk.Button(nav_buttons_frame, text="Próxima Palavra", command=self.next_word,
                                     font=tkFont.Font(family="Arial", size=10), bg="#28A745", fg="white",
                                     padx=15, pady=8, relief="raised", bd=2)
        self.next_button.grid(row=0, column=1, padx=5)

    def on_closing(self):
        # Ao fechar a janela de avaliação, reativa a janela principal
        self.master.grab_release()
        self.avaliacao_window.destroy()

    def display_current_word(self):
        if self.current_word_index < len(self.palavras_icones):
            palavra_info = self.palavras_icones[self.current_word_index]
            palavra = palavra_info['palavra']
            icone = palavra_info['icone']

            self.icon_label.config(text=icone)
            self.progress_label.config(text=f"Palavra {self.current_word_index + 1} de {len(self.palavras_icones)}")
            self.child_entry_var.set("") # Limpa o campo de entrada
            self.analysis_text.config(state="normal")
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.config(state="disabled")

            self.generate_letter_bank(palavra)
            self.update_navigation_buttons()
        else:
            self.show_final_analysis()

    def generate_letter_bank(self, correct_word):
        # Limpa botões antigos
        for widget in self.letter_buttons_container.winfo_children():
            widget.destroy()

        # Todas as letras da palavra correta
        letters = list(correct_word.lower())
# parte 
        # Adiciona 5 letras extras aleatórias
        for _ in range(5):
            letters.append(random.choice(string.ascii_lowercase))

        random.shuffle(letters) # Embaralha as letras

        # Cria os botões
        col_count = 0
        row_count = 0
        for i, char in enumerate(letters):
            btn = tk.Button(self.letter_buttons_container, text=char.upper(),
                            font=tkFont.Font(family="Arial", size=16, weight="bold"),
                            command=lambda c=char: self.append_to_entry(c),
                            width=3, height=1, relief="raised", bd=2, bg="#E0E8F9", fg="#4A6CD2")
            btn.grid(row=row_count, column=col_count, padx=3, pady=3)
            col_count += 1
            if col_count > 6: # 7 botões por linha para tela móvel
                col_count = 0
                row_count += 1
        
        # Configurar colunas do container de botões para expandir
        for c in range(col_count + 1): # Ajuste para o número real de colunas usadas
            self.letter_buttons_container.grid_columnconfigure(c, weight=1)


    def append_to_entry(self, char):
        current_text = self.child_entry_var.get()
        self.child_entry_var.set(current_text + char)
        self.validate_input() # Valida após cada adição

    def validate_input(self, event=None):
        current_text = self.child_entry_var.get()
        # Aceita apenas letras (a-z, A-Z)
        filtered_text = "".join(filter(str.isalpha, current_text))
        if filtered_text != current_text:
            self.child_entry_var.set(filtered_text)
            # Opcional: mostrar um aviso se caracteres inválidos forem removidos
            # messagebox.showwarning("Aviso", "Apenas letras são permitidas.")

        # Realiza a análise sempre que o input muda
        self.perform_analysis()

    def perform_analysis(self):
        palavra_info = self.palavras_icones[self.current_word_index]
        palavra_correta = palavra_info['palavra'].lower()
        input_crianca = self.child_entry_var.get().lower()
        
        analysis_output, hypothesis_type, scores = self.analisar_escrita(palavra_correta, input_crianca)
        
        self.analysis_text.config(state="normal")
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, analysis_output)
        self.analysis_text.config(state="disabled")

        # Armazena o input e o resultado da análise para a palavra atual
        if len(self.child_input_history) <= self.current_word_index:
            self.child_input_history.append(input_crianca)
            self.analysis_results_history.append({
                'input': input_crianca,
                'analysis_text': analysis_output,
                'hypothesis': hypothesis_type,
                'scores': scores
            })
        else:
            self.child_input_history[self.current_word_index] = input_crianca
            self.analysis_results_history[self.current_word_index] = {
                'input': input_crianca,
                'analysis_text': analysis_output,
                'hypothesis': hypothesis_type,
                'scores': scores
            }

    def count_syllables(self, word):
        """
        Aproximação simples da contagem de sílabas baseada em grupos de vogais.
        Considera vogais acentuadas.
        """
        vowels = "aeiouáéíóúàèìòùãõ"
        count = 0
        in_vowel_group = False
        for char in word.lower():
            if char in vowels:
                if not in_vowel_group:
                    count += 1
                    in_vowel_group = True
            else:
                in_vowel_group = False
        return max(1, count) # Garante pelo menos 1 sílaba

    def analisar_escrita(self, palavra_correta, input_crianca):
        """
        Função para analisar a escrita da criança com base nas diferentes hipóteses.
        Retorna uma string com a análise detalhada, o tipo de hipótese predominante
        para esta palavra e um dicionário de scores para cada hipótese.
        """
        scores = {
            'Pré-silábica': 0,
            'Silábica com Valor de Vogal': 0,
            'Silábica com Valor de Consoante': 0,
            'Silábico-Alfabética': 0,
            'Alfabética': 0
        }
        analise_detalhada = []
        hipotese_classificacao = "Não Classificado"

        # --- Métricas Básicas ---
        input_len = len(input_crianca)
        correct_len = len(palavra_correta)
        
        vogais_pt = "aeiouáéíóúàèìòùãõ"
        consoantes_pt = "bcdfghjklmnpqrstvwxyz" # Simplificado, não inclui ç, etc.

        input_vowels = [c for c in input_crianca if c in vogais_pt]
        input_consonants = [c for c in input_crianca if c in consoantes_pt]

        correct_word_vowels = [c for c in palavra_correta if c in vogais_pt]
        correct_word_consonants = [c for c in palavra_correta if c in consoantes_pt]

        num_syllables_correct = self.count_syllables(palavra_correta)

        # --- 1. Alfabética ---
        if input_crianca == palavra_correta:
            scores['Alfabética'] = 100 # Pontuação máxima para escrita correta
            analise_detalhada.append("- Escrita alfabética (correta).")
            hipotese_classificacao = "Alfabética"
            return "\n".join(analise_detalhada), hipotese_classificacao, scores

        # --- 2. Pré-silábica ---
        ps_score_current = 0
        letras_corretas_set = set(palavra_correta)
        letras_aleatorias = [char for char in input_crianca if char not in letras_corretas_set and char.isalpha()]
        if letras_aleatorias:
            analise_detalhada.append(f"- Pré-silábica: Letras aleatórias detectadas: {' '.join(letras_aleatorias)}")
            ps_score_current += 2

        if input_len == 0:
            analise_detalhada.append("- Pré-silábica: Nenhuma letra digitada.")
            ps_score_current += 3
        elif input_len < correct_len / 2:
            analise_detalhada.append(f"- Pré-silábica: Quantidade de letras muito reduzida ({input_len} vs {correct_len} esperadas).")
            ps_score_current += 2
        elif input_len > correct_len * 1.5:
            analise_detalhada.append(f"- Pré-silábica: Quantidade de letras excessiva ({input_len} vs {correct_len} esperadas).")
            ps_score_current += 1

        contagem_letras = Counter(input_crianca)
        letras_repetidas_excessivamente = [char for char, count in contagem_letras.items() if count > 2 and char.isalpha()]
        if letras_repetidas_excessivamente:
            analise_detalhada.append(f"- Pré-silábica: Repetições excessivas da(s) letra(s): {' '.join(letras_repetidas_excessivamente)}")
            ps_score_current += 2

        non_alphabetic_chars = [char for char in input_crianca if not char.isalpha()]
        if non_alphabetic_chars:
            analise_detalhada.append(f"- Pré-silábica: Números ou símbolos detectados: {' '.join(non_alphabetic_chars)}")
            ps_score_current += 3

        tem_vogal_input = any(char in vogais_pt for char in input_crianca)
        tem_consoante_input = any(char in consoantes_pt for char in input_crianca)
        
        if input_crianca and not tem_vogal_input and tem_consoante_input:
            analise_detalhada.append("- Pré-silábica: Uso exclusivo de consoantes.")
            ps_score_current += 2
        if input_crianca and not tem_consoante_input and tem_vogal_input:
            analise_detalhada.append("- Pré-silábica: Uso exclusivo de vogais.")
            ps_score_current += 2
        
        if input_len > 0 and input_len < 3 and not any(char in palavra_correta for char in input_crianca):
            analise_detalhada.append("- Pré-silábica: Escrita muito curta e sem correspondência aparente com a palavra correta.")
            ps_score_current += 2
        
        scores['Pré-silábica'] = ps_score_current

        # --- 3. Silábica com Valor de Vogal (SVV) ---
        svv_score_current = 0
        # Se o número de letras é próximo ao número de sílabas
        if input_len > 0 and abs(input_len - num_syllables_correct) <= 1:
            # Verifica se a maioria das letras são vogais e se essas vogais estão na palavra correta
            if len(input_vowels) > 0 and (len(input_vowels) / input_len) >= 0.7:
                vowel_match_in_correct = sum(1 for v in input_vowels if v in correct_word_vowels)
                if len(input_vowels) > 0 and (vowel_match_in_correct / len(input_vowels)) >= 0.5: # Pelo menos 50% das vogais digitadas estão na palavra
                    svv_score_current += 50
                    analise_detalhada.append("- Silábica com Valor de Vogal: Número de letras próximo ao de sílabas, com predominância de vogais com valor sonoro.")
        scores['Silábica com Valor de Vogal'] = svv_score_current

        # --- 4. Silábica com Valor de Consoante (SVC) ---
        svc_score_current = 0
        # Se o número de letras é próximo ao número de sílabas
        if input_len > 0 and abs(input_len - num_syllables_correct) <= 1:
            # Verifica se a maioria das letras são consoantes e se essas consoantes estão na palavra correta
            if len(input_consonants) > 0 and (len(input_consonants) / input_len) >= 0.7:
                consonant_match_in_correct = sum(1 for c in input_consonants if c in correct_word_consonants)
                if len(input_consonants) > 0 and (consonant_match_in_correct / len(input_consonants)) >= 0.5: # Pelo menos 50% das consoantes digitadas estão na palavra
                    svc_score_current += 50
                    analise_detalhada.append("- Silábica com Valor de Consoante: Número de letras próximo ao de sílabas, com predominância de consoantes com valor sonoro.")
        scores['Silábica com Valor de Consoante'] = svc_score_current

        # --- 5. Silábico-Alfabética ---
        sa_score_current = 0
        matched_chars_in_order = 0
        for i in range(min(input_len, correct_len)):
            if input_crianca[i] == palavra_correta[i]:
                matched_chars_in_order += 1
        
        # Se há uma correspondência parcial e o comprimento está mais próximo do correto
        if correct_len > 0 and (matched_chars_in_order / correct_len) >= 0.3 and (matched_chars_in_order / correct_len) < 1.0:
            if abs(input_len - correct_len) <= 2: # Tolerância de 2 letras
                sa_score_current += 70
                analise_detalhada.append("- Silábico-Alfabética: Escrita com algumas correspondências corretas e aproximação da forma alfabética.")
        scores['Silábico-Alfabética'] = sa_score_current


        # Determina a classificação principal para exibição nesta palavra
        # Prioridade: Alfabética > Silábico-Alfabética > SVV/SVC > Pré-silábica > Não Classificado
        if scores['Alfabética'] > 0:
            hipotese_classificacao = "Alfabética"
        elif scores['Silábico-Alfabética'] > 0:
            hipotese_classificacao = "Silábico-Alfabética"
       
       
        elif scores['Silábica com Valor de Vogal'] > 0 and scores['Silábica com Valor de Vogal'] >= scores['Silábica com Valor de Consoante']:
            hipotese_classificacao = "Silábica com Valor de Vogal"
        elif scores['Silábica com Valor de Consoante'] > 0:
            hipotese_classificacao = "Silábica com Valor de Consoante"
        elif scores['Pré-silábica'] > 0:
            hipotese_classificacao = "Pré-silábica"
        elif input_len > 0 and abs(input_len - num_syllables_correct) <= 1: # Se não encaixou em SVV/SVC mas comprimento é silábico
            hipotese_classificacao = "Silábica (Geral)"
            analise_detalhada.append("- Silábica (Geral): Número de letras próximo ao número de sílabas, mas sem valor de vogal/consoante claro.")
        else:
            hipotese_classificacao = "Não Classificado"

# 👉 Regra extra: Forçar Silábica para palavras com ≥3 sílabas e escrita muito reduzida
if num_syllables_correct >= 3:
    if input_len == 1 and input_crianca[0] in palavra_correta:
        # Só uma letra válida, mas insuficiente para classificação avançada
        if hipotese_classificacao in ["Alfabética", "Silábico-Alfabética"]:
            hipotese_classificacao = "Silábica (Geral)"
            analise_detalhada.append("- Regra pedagógica aplicada: Palavra longa com resposta muito curta. Reclassificada como Silábica.")



            if not analise_detalhada and input_crianca:
                analise_detalhada.append("- Não foram detectadas características típicas das hipóteses específicas com base nas regras atuais. A escrita pode ser muito incipiente ou em transição.")
            elif not input_crianca:
                analise_detalhada.append("- Nenhuma letra digitada.")

         # Garante que a análise detalhada não esteja vazia se a classificação for "Não Classificado"
    if hipotese_classificacao == "Não Classificado" and not analise_detalhada:
        analise_detalhada.append("- A escrita não se encaixa claramente em nenhuma hipótese específica com as regras atuais.")
    
    final_output = f"Hipótese Classificada: {hipotese_classificacao}\n\nCaracterísticas Observadas:\n" + "\n".join(analise_detalhada)
    return final_output, hipotese_classificacao, scores

def next_word(self):
    # Garante que a análise da palavra atual seja salva antes de prosseguir
    resultado, classificacao, pontuacoes = self.perform_analysis()
    # Aqui você pode decidir o que fazer com esses dados
    self.current_word_index += 1
    if self.current_word_index < len(self.palavras_icones):
        self.display_current_word()
    else:
        self.show_final_analysis()

        self.current_word_index += 1
        if self.current_word_index < len(self.palavras_icones):
            self.display_current_word()
        else:
            self.show_final_analysis()

    def prev_word(self):
        if self.current_word_index > 0:
            self.current_word_index -= 1
            self.display_current_word()
            # Recarrega o input anterior e a análise se houver
            if len(self.child_input_history) > self.current_word_index:
                self.child_entry_var.set(self.child_input_history[self.current_word_index])
                self.analysis_text.config(state="normal")
                self.analysis_text.delete(1.0, tk.END)
                self.analysis_text.insert(tk.END, self.analysis_results_history[self.current_word_index]['analysis_text'])
                self.analysis_text.config(state="disabled")

    def update_navigation_buttons(self):
        self.prev_button.config(state="normal" if self.current_word_index > 0 else "disabled")
        self.next_button.config(text="Próxima Palavra" if self.current_word_index < len(self.palavras_icones) - 1 else "Finalizar Avaliação")


    def show_final_analysis(self):
        self.avaliacao_window.grab_release()
        self.avaliacao_window.destroy() # Fecha a janela de avaliação individual

        FinalAnalysisScreen(self.master, self.palavras_icones, self.analysis_results_history)


# Classe para a tela de resultados e feedback
class FinalAnalysisScreen:
    def __init__(self, master, palavras_icones, analysis_results_history):
        self.master = master
        self.palavras_icones = palavras_icones
        self.analysis_results_history = analysis_results_history
        # Adiciona 'Silábica (Geral)' à lista de todas as hipóteses para garantir que seja contada
        self.all_hypotheses = ['Pré-silábica', 'Silábica com Valor de Vogal', 'Silábica com Valor de Consoante', 'Silábica (Geral)', 'Silábico-Alfabética', 'Alfabética']

        self.setup_ui()
        self.perform_final_analysis()

    def setup_ui(self):
        self.final_window = tk.Toplevel(self.master)
        self.final_window.title("Escrevilândia: Análise Geral")
        self.final_window.geometry("500x750") # Tamanho ajustado para a tela de resultados
        self.final_window.resizable(True, True)
        self.final_window.transient(self.master)
        self.final_window.grab_set()
        self.final_window.focus_set()
        self.final_window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.final_window.grid_rowconfigure(0, weight=1) # Main scrollable frame
        self.final_window.grid_columnconfigure(0, weight=1)

        # Main scrollable area
        canvas = tk.Canvas(self.final_window, bg="#F0F2F5", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.final_window, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.scrollable_content_frame = tk.Frame(canvas, bg="#F0F2F5", padx=15, pady=15)
        canvas.create_window((0, 0), window=self.scrollable_content_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas.winfo_children()[0], width=canvas.winfo_width())

        self.scrollable_content_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_frame_configure)

        # --- Nível de Escrita Identificado ---
        level_frame = tk.Frame(self.scrollable_content_frame, bg="white", bd=1, relief="solid", padx=10, pady=10)
        level_frame.pack(fill="x", pady=(0, 15))
        level_frame.grid_columnconfigure(0, weight=1)

        tk.Label(level_frame, text="Nível de Escrita Identificado", font=tkFont.Font(family="Arial", size=14, weight="bold"), bg="white", fg="#5D3FD3").grid(row=0, column=0, pady=(0, 5))
        self.predominant_hypothesis_label = tk.Label(level_frame, text="", font=tkFont.Font(family="Arial", size=18, weight="bold"), bg="white", fg="#333333")
        self.predominant_hypothesis_label.grid(row=1, column=0, pady=(0, 10))

        # --- Precisão Geral ---
        accuracy_frame = tk.Frame(level_frame, bg="white", padx=5, pady=5)
        accuracy_frame.grid(row=2, column=0, sticky="ew")
        accuracy_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(accuracy_frame, text="Precisão Geral", font=tkFont.Font(family="Arial", size=12, weight="bold"), bg="white", anchor="w").grid(row=0, column=0, sticky="w")
        
        self.accuracy_bar_container = tk.Frame(accuracy_frame, bg="#E0E0E0", height=10, relief="flat", bd=0)
        self.accuracy_bar_container.grid(row=1, column=0, sticky="ew", pady=(5,0))
        self.accuracy_bar_container.grid_columnconfigure(0, weight=1) # For the inner bar

        self.accuracy_bar = tk.Frame(self.accuracy_bar_container, bg="#4CAF50", height=10, relief="flat", bd=0)
        self.accuracy_bar.grid(row=0, column=0, sticky="w") # Will be updated with width

        self.accuracy_percentage_label = tk.Label(accuracy_frame, text="0%", font=tkFont.Font(family="Arial", size=10), bg="white", fg="#666666", anchor="e")
        self.accuracy_percentage_label.grid(row=0, column=0, sticky="e")


        # --- Análise por Palavra ---
        word_analysis_frame = tk.Frame(self.scrollable_content_frame, bg="white", bd=1, relief="solid", padx=10, pady=10)
        word_analysis_frame.pack(fill="x", pady=(0, 15))
        word_analysis_frame.grid_columnconfigure(0, weight=1)

        tk.Label(word_analysis_frame, text="Análise por Palavra", font=tkFont.Font(family="Arial", size=14, weight="bold"), bg="white", fg="#333333").grid(row=0, column=0, pady=(0, 5))
        self.word_analysis_container = tk.Frame(word_analysis_frame, bg="white")
        self.word_analysis_container.grid(row=1, column=0, sticky="nsew")
        self.word_analysis_container.grid_columnconfigure(0, weight=1)


        # --- Distribuição de Hipóteses ---
        distribution_frame = tk.Frame(self.scrollable_content_frame, bg="white", bd=1, relief="solid", padx=10, pady=10)
        distribution_frame.pack(fill="x", pady=(0, 15))
        distribution_frame.grid_columnconfigure(0, weight=1)

        tk.Label(distribution_frame, text="Distribuição de Hipóteses", font=tkFont.Font(family="Arial", size=14, weight="bold"), bg="white", fg="#333333").grid(row=0, column=0, pady=(0, 5))
        self.hypothesis_distribution_container = tk.Frame(distribution_frame, bg="white")
        self.hypothesis_distribution_container.grid(row=1, column=0, sticky="nsew")
        self.hypothesis_distribution_container.grid_columnconfigure(0, weight=1) # Label for hypothesis name
        self.hypothesis_distribution_container.grid_columnconfigure(1, weight=0) # Count
        self.hypothesis_distribution_container.grid_columnconfigure(2, weight=1) # Bar
        self.hypothesis_distribution_container.grid_columnconfigure(3, weight=0) # Percentage


        # --- Feedback Personalizado (Criança) ---
        feedback_frame = tk.Frame(self.scrollable_content_frame, bg="white", bd=1, relief="solid", padx=10, pady=10)
        feedback_frame.pack(fill="x", pady=(0, 15))
        feedback_frame.grid_columnconfigure(0, weight=1)

        self.feedback_title_label = tk.Label(feedback_frame, text="Sua Escrita 'Mora' Principalmente em...", font=tkFont.Font(family="Arial", size=16, weight="bold"), bg="white", fg="#5D3FD3")
        self.feedback_title_label.grid(row=0, column=0, pady=(0, 5))
        self.feedback_message_label = tk.Label(feedback_frame, text="", font=tkFont.Font(family="Arial", size=12), bg="white", fg="#333333", wraplength=450, justify="center")
        self.feedback_message_label.grid(row=1, column=0, pady=(0, 10))


        # --- Recomendações Pedagógicas ---
        reco_frame = tk.Frame(self.scrollable_content_frame, bg="white", bd=1, relief="solid", padx=10, pady=10)
        reco_frame.pack(fill="x", pady=(0, 15))
        reco_frame.grid_columnconfigure(0, weight=1)

        tk.Label(reco_frame, text="Recomendações Pedagógicas", font=tkFont.Font(family="Arial", size=14, weight="bold"), bg="white", fg="#333333").grid(row=0, column=0, pady=(0, 5))
        self.recommendations_text = tk.Text(reco_frame, font=tkFont.Font(family="Arial", size=10), bg="#F9F9F9", wrap="word", height=8, bd=0, relief="flat")
        self.recommendations_text.grid(row=1, column=0, sticky="nsew", pady=(5,0))
        self.recommendations_text.config(state="disabled")


        # --- Botão Fechar ---
        tk.Button(self.scrollable_content_frame, text="Fechar Análise", command=self.on_closing,
                  font=tkFont.Font(family="Arial", size=10), bg="#DC3545", fg="white",
                  padx=15, pady=8, relief="raised", bd=2).pack(pady=10)


    def on_closing(self):
        self.master.grab_release()
        self.final_window.destroy()

    def calculate_word_accuracy(self, correct_word, child_input):
        """Calcula uma porcentagem de 'acurácia' baseada na correspondência de caracteres."""
        correct_word_lower = correct_word.lower()
        child_input_lower = child_input.lower()

        if not child_input_lower:
            return 0.0

        matched_chars = 0
        for i in range(min(len(correct_word_lower), len(child_input_lower))):
            if correct_word_lower[i] == child_input_lower[i]:
                matched_chars += 1
        
        # Penaliza entradas muito longas ou muito curtas em relação à palavra correta
        # Usamos o máximo entre o comprimento da palavra correta e o input para o divisor
        # para penalizar inputs muito longos ou muito curtos.
        max_len = max(len(correct_word_lower), len(child_input_lower))
        if max_len == 0: return 0.0 # Evita divisão por zero
        
        return (matched_chars / max_len) * 100

    def perform_final_analysis(self):
        # Alterado para contar a ocorrência de cada hipótese principal
        total_hypothesis_counts = Counter({h: 0 for h in self.all_hypotheses})
        total_accuracy_sum = 0
        
        # Preencher Análise por Palavra
        for i, result in enumerate(self.analysis_results_history):
            palavra_info = self.palavras_icones[i]
            palavra_correta = palavra_info['palavra']
            input_crianca = result['input']
            hipotese = result['hypothesis'] # A hipótese principal classificada para esta palavra
            analysis_text = result['analysis_text']
            scores = result['scores']

            # Incrementa a contagem para a hipótese principal desta palavra
            total_hypothesis_counts[hipotese] += 1
            
            # Calcular acurácia para esta palavra
            word_accuracy = self.calculate_word_accuracy(palavra_correta, input_crianca)
            total_accuracy_sum += word_accuracy

            # UI para Análise por Palavra
            word_frame = tk.Frame(self.word_analysis_container, bg="#F9F9F9", bd=1, relief="flat", padx=10, pady=8)
            word_frame.pack(fill="x", pady=5)
            word_frame.grid_columnconfigure(0, weight=1) # Palavra e Escrita
            word_frame.grid_columnconfigure(1, weight=0) # Porcentagem
            word_frame.grid_columnconfigure(2, weight=0) # Hipótese

            tk.Label(word_frame, text=f"Palavra {i+1}: {palavra_correta.upper()}", font=tkFont.Font(family="Arial", size=11, weight="bold"), bg="#F9F9F9", anchor="w").grid(row=0, column=0, sticky="w")
            tk.Label(word_frame, text=f"Escrita: {input_crianca if input_crianca else '____'}", font=tkFont.Font(family="Arial", size=10), bg="#F9F9F9", anchor="w").grid(row=1, column=0, sticky="w")
            
            tk.Label(word_frame, text=f"{word_accuracy:.0f}%", font=tkFont.Font(family="Arial", size=10, weight="bold"), bg="#F9F9F9", fg="#4CAF50").grid(row=0, column=1, sticky="e", padx=5)
            tk.Label(word_frame, text=f"{hipotese}", font=tkFont.Font(family="Arial", size=9), bg="#E0E8F9", fg="#4A6CD2", relief="solid", bd=1, padx=5, pady=2).grid(row=1, column=1, sticky="e", padx=5)

            # Barra de progresso para a palavra
            word_progress_bar_container = tk.Frame(word_frame, bg="#E0E0E0", height=5, relief="flat", bd=0)
            word_progress_bar_container.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(5,0))
            word_progress_bar_container.grid_columnconfigure(0, weight=1)

            word_progress_bar = tk.Frame(word_progress_bar_container, bg="#4CAF50", height=5, relief="flat", bd=0)
            word_progress_bar_width = int((word_accuracy / 100) * word_progress_bar_container.winfo_width()) # Initial width
            word_progress_bar.grid(row=0, column=0, sticky="w")
            word_progress_bar.grid_propagate(False) # Prevent bar from resizing itself
            word_progress_bar.config(width=word_progress_bar_width)
            
            # Update width on configure
            def update_bar_width(event, bar=word_progress_bar, container=word_progress_bar_container, acc=word_accuracy):
                new_width = int((acc / 100) * container.winfo_width())
                bar.config(width=new_width)
            word_progress_bar_container.bind("<Configure>", update_bar_width)


        # --- Calcular e Exibir Precisão Geral ---
        overall_accuracy = (total_accuracy_sum / len(self.palavras_icones)) if self.palavras_icones else 0
        self.accuracy_percentage_label.config(text=f"{overall_accuracy:.0f}%")
        
        # Update General Accuracy Bar
        def update_general_bar_width(event, bar=self.accuracy_bar, container=self.accuracy_bar_container, acc=overall_accuracy):
            new_width = int((acc / 100) * container.winfo_width())
            bar.config(width=new_width)
        self.accuracy_bar_container.bind("<Configure>", update_general_bar_width)
        self.accuracy_bar.grid_propagate(False)
        self.accuracy_bar.config(width=int((overall_accuracy / 100) * self.accuracy_bar_container.winfo_width()))


        # --- Calcular e Exibir Distribuição de Hipóteses ---
        # Agora baseia-se na contagem de palavras classificadas em cada hipótese
        total_words_evaluated = len(self.palavras_icones)
        hypothesis_percentages = {h: 0.0 for h in self.all_hypotheses}
        if total_words_evaluated > 0:
            for hyp_name in self.all_hypotheses:
                hypothesis_percentages[hyp_name] = (total_hypothesis_counts[hyp_name] / total_words_evaluated) * 100
        
        # Determinar a hipótese predominante geral com base na contagem
        predominant_hypothesis = "Não Classificado"
        if total_words_evaluated > 0:
            # Encontra a hipótese com a maior contagem
            max_count = -1
            for hyp_name in self.all_hypotheses:
                if total_hypothesis_counts[hyp_name] > max_count:
                    max_count = total_hypothesis_counts[hyp_name]
                    predominant_hypothesis = hyp_name
                # Lida com empates, priorizando alfabética > silábico-alfabética > silábica > pré-silábica
                elif total_hypothesis_counts[hyp_name] == max_count:
                    # Implementar ordem de prioridade para desempate se necessário
                    # Exemplo simples de prioridade (pode ser ajustado):
                    priority_order = {
                        'Alfabética': 5,
                        'Silábico-Alfabética': 4,
                        'Silábica com Valor de Vogal': 3,
                        'Silábica com Valor de Consoante': 3,
                        'Silábica (Geral)': 2,
                        'Pré-silábica': 1,
                        'Não Classificado': 0
                    }
                    if priority_order.get(hyp_name, 0) > priority_order.get(predominant_hypothesis, 0):
                        predominant_hypothesis = hyp_name
            
            if max_count == 0: # Se todas as contagens são zero (ex: nenhuma palavra digitada)
                predominant_hypothesis = "Não Classificado"
        
        self.predominant_hypothesis_label.config(text=predominant_hypothesis)

        row_idx = 0
        for hyp_name in self.all_hypotheses:
            percent = hypothesis_percentages[hyp_name]
            count = total_hypothesis_counts[hyp_name]

            tk.Label(self.hypothesis_distribution_container, text=hyp_name, font=tkFont.Font(family="Arial", size=10), bg="white", anchor="w").grid(row=row_idx, column=0, sticky="w", pady=2)
            tk.Label(self.hypothesis_distribution_container, text=f"{count}", font=tkFont.Font(family="Arial", size=10), bg="white").grid(row=row_idx, column=1, sticky="w", padx=5)
            
            # Barra de progresso para a distribuição
            bar_container = tk.Frame(self.hypothesis_distribution_container, bg="#E0E0E0", height=10, relief="flat", bd=0)
            bar_container.grid(row=row_idx, column=2, sticky="ew", padx=5)
            bar_container.grid_columnconfigure(0, weight=1)

            bar = tk.Frame(bar_container, bg="#4A6CD2", height=10, relief="flat", bd=0)
            bar_width = int((percent / 100) * bar_container.winfo_width()) # Initial width
            bar.grid(row=0, column=0, sticky="w")
            bar.grid_propagate(False)
            bar.config(width=bar_width)

            # Update width on configure
            def update_dist_bar_width(event, b=bar, bc=bar_container, p=percent):
                new_width = int((p / 100) * bc.winfo_width())
                b.config(width=new_width)
            bar_container.bind("<Configure>", update_dist_bar_width)


            tk.Label(self.hypothesis_distribution_container, text=f"{percent:.0f}%", font=tkFont.Font(family="Arial", size=10), bg="white").grid(row=row_idx, column=3, sticky="e")
            row_idx += 1


        # --- Feedback Personalizado (Criança) ---
        feedback_message = ""
        if predominant_hypothesis == "Alfabética":
            feedback_message = "Uau! Sua escrita já está super parecida com a dos livros! Você é um(a) craque das letras e um(a) grande escritor(a)!"
        elif predominant_hypothesis == "Silábico-Alfabética":
            feedback_message = "Que incrível! Você já está misturando os sons e as letras muito bem! Cada letrinha que você aprende te deixa mais perto de escrever como um(a) escritor(a) de verdade! Continue assim!"
        elif predominant_hypothesis in ["Silábica com Valor de Vogal", "Silábica com Valor de Consoante", "Silábica (Geral)"]:
            feedback_message = "Muito bem! Você está começando a perceber os sons das palavras e a usar as letras para representá-los. Continue explorando as letras e os sons, você está no caminho certo para escrever cada vez melhor!"
        elif predominant_hypothesis == "Pré-silábica":
            feedback_message = "Sua curiosidade é fantástica! Você está explorando o mundo das letras e já está criando suas próprias marcas. Continue brincando com as letras e logo você vai descobrir como elas formam as palavras!"
        else:
            feedback_message = "Sua jornada na escrita está apenas começando! Cada tentativa te deixa mais perto de descobrir os segredos das letras. Continue explorando e se divertindo!"
        
        self.feedback_message_label.config(text=feedback_message)

        # --- Recomendações Pedagógicas ---
        recommendations = []
        if predominant_hypothesis == "Pré-silábica":
            recommendations = [
                "- Trabalhar com o nome próprio da criança.",
                "- Explorar letras do alfabeto através de jogos.",
                "- Atividades de consciência fonológica (rimas, aliterações).",
                "- Leitura diária de histórias.",
                "- Brincadeiras com sons das palavras."
            ]
        elif predominant_hypothesis in ["Silábica com Valor de Vogal", "Silábica com Valor de Consoante", "Silábica (Geral)"]:
            recommendations = [
                "- Focar na relação entre som e letra (fonema-grafema).",
                "- Atividades de segmentação de sílabas.",
                "- Jogos com sílabas iniciais, mediais e finais.",
                "- Escrita de pequenas listas de palavras conhecidas.",
                "- Incentivar a escrita espontânea, mesmo que com poucas letras."
            ]
        elif predominant_hypothesis == "Silábico-Alfabética":
            recommendations = [
                "- Atividades de análise e síntese de palavras.",
                "- Ditado de palavras com diferentes estruturas silábicas.",
                "- Leitura de textos curtos e simples.",
                "- Produção de pequenos textos com apoio (ex: legendas de desenhos).",
                "- Jogos de completar palavras com letras faltantes."
            ]
        elif predominant_hypothesis == "Alfabética":
            recommendations = [
                "- Incentivar a leitura e escrita de textos mais complexos.",
                "- Atividades de revisão e correção ortográfica.",
                "- Produção de textos mais elaborados (contos, cartas).",
                "- Exploração de diferentes gêneros textuais.",
                "- Jogos de palavras e desafios de vocabulário."
            ]
        else: # Default recommendations
            recommendations = [
                "- Continue incentivando a criança a explorar a escrita de forma lúdica.",
                "- Ofereça um ambiente rico em materiais de leitura e escrita.",
                "- Celebre cada pequena conquista na jornada da escrita."
            ]

        self.recommendations_text.config(state="normal")
        self.recommendations_text.delete(1.0, tk.END)
        self.recommendations_text.insert(tk.END, "\n".join(recommendations))
        self.recommendations_text.config(state="disabled")


# --- Funções da tela principal (existente) ---
def criar_interface():
    root = tk.Tk()
    root.title("Escrevilândia: A terra da escrita")
    root.geometry("400x700")
    root.resizable(True, True)
    root.configure(bg="#F0F2F5")

    titulo_font = tkFont.Font(family="Arial", size=20, weight="bold")
    subtitulo_font = tkFont.Font(family="Arial", size=12)
    secao_font = tkFont.Font(family="Arial", size=14, weight="bold")
    instrucao_font = tkFont.Font(family="Arial", size=11)
    label_palavra_font = tkFont.Font(family="Arial", size=11, weight="bold")
    entrada_font = tkFont.Font(family="Arial", size=11)
    botao_font = tkFont.Font(family="Arial", size=9)
    emoji_font = tkFont.Font(family="Segoe UI Emoji", size=18)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    canvas = tk.Canvas(root, bg="#F0F2F5", highlightthickness=0)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    scrollable_frame = tk.Frame(canvas, bg="#F0F2F5")
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(canvas.winfo_children()[0], width=canvas.winfo_width())

    scrollable_frame.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_frame_configure)

    header_frame = tk.Frame(scrollable_frame, bg="#F0F2F5", pady=15)
    header_frame.pack(fill="x", padx=10, pady=10)
    header_frame.grid_columnconfigure(0, weight=1)

    title_label = tk.Label(header_frame,
                           text="Escrevilândia: A terra da escrita",
                           font=titulo_font,
                           fg="#5D3FD3",
                           bg="#F0F2F5")
    title_label.pack()

    subtitle_label = tk.Label(header_frame,
                              text="Preparação para avaliação da escrita infantil",
                              font=subtitulo_font,
                              fg="#666666",
                              bg="#F0F2F5")
    subtitle_label.pack(pady=3)

    content_area_frame = tk.Frame(scrollable_frame, bg="white", bd=1, relief="solid", padx=15, pady=15)
    content_area_frame.pack(pady=10, padx=15, fill="x", expand=False)

    content_area_frame.grid_columnconfigure(0, weight=0)
    content_area_frame.grid_columnconfigure(1, weight=3)
    content_area_frame.grid_columnconfigure(2, weight=1)

    for i in range(4):
        content_area_frame.grid_rowconfigure(2 + i * 2, weight=0)
        content_area_frame.grid_rowconfigure(2 + i * 2 + 1, weight=1)

    section_title = tk.Label(content_area_frame, text="Entrada de Palavras", font=secao_font, fg="#333333", bg="white", anchor="w")
    section_title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

    instructions_label = tk.Label(content_area_frame,
                                  text="Professor(a), por favor, digite quatro palavras que a criança irá escrever. "
                                       "Para cada palavra, escolha um ícone ou emoji que a represente bem.",
                                  font=instrucao_font,
                                  fg="#555555",
                                  bg="white",
                                  wraplength=350,
                                  justify="left",
                                  anchor="w")
    instructions_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 15))

    entradas_palavras = []
    icones_palavras_var = []
    botoes_icone_refs = []

    emojis_disponiveis = [
        "😀", "🚀", "💡", "📚", "🍎", "🏠", "🐱", "🐶", "🌳", "☀️",
        "🌈", "⚽", "🚗", "⏰", "🍕", "💙", "🌟", "🎈", "💧", "🔑",
        "💻", "📱", "🌎", "❤️", "👍", "👎", "😊", "�", "😢", "🎉",
        "✨", "💫", "🎶", "🎵", "❓", "❗", "✅", "❌", "⬆️", "⬇️",
        "✅", "❌", "⬆️", "⬇️", "👍", "👎", "😊", "😂", "😢", "🎉",
        "✨", "💫", "🎶", "🎵", "❓", "❗", "🍎", "🏠", "🐱", "🐶",
        "🌳", "☀️", "🌈", "⚽", "🚗", "⏰", "🍕", "💙", "🌟", "🎈",
        "💧", "🔑", "💻", "📱", "🌎", "❤️", "😀", "🚀", "💡", "📚",
        "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥",
        "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥",
        "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥",
        "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥",
        "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥",
        "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥",
        "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥",
        "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥",
        "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥",
        "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥",
        "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥",
        "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥", "💯", "🔥",
    ]

    def abrir_seletor_icone(index):
        seletor_window = tk.Toplevel(root)
        seletor_window.title(f"Escolha um Ícone para a Palavra {index + 1}")
        seletor_window.geometry("350x450")
        seletor_window.transient(root)
        seletor_window.grab_set()
        seletor_window.focus_set()
        seletor_window.resizable(False, False)

        seletor_window.grid_rowconfigure(0, weight=1)
        seletor_window.grid_rowconfigure(1, weight=0)
        seletor_window.grid_rowconfigure(2, weight=0)
        seletor_window.grid_columnconfigure(0, weight=1)

        emoji_canvas = tk.Canvas(seletor_window, bg=seletor_window.cget('bg'), highlightthickness=0)
        emoji_scrollbar = tk.Scrollbar(seletor_window, orient="vertical", command=emoji_canvas.yview)
        emoji_canvas.configure(yscrollcommand=emoji_scrollbar.set)

        emoji_canvas.grid(row=0, column=0, sticky="nsew")
        emoji_scrollbar.grid(row=0, column=1, sticky="ns")

        emoji_frame = tk.Frame(emoji_canvas, padx=5, pady=5, bg=seletor_window.cget('bg'))
        emoji_canvas.create_window((0, 0), window=emoji_frame, anchor="nw")

        def on_emoji_frame_configure(event):
            emoji_canvas.configure(scrollregion=emoji_canvas.bbox("all"))
            emoji_canvas.itemconfig(emoji_canvas.winfo_children()[0], width=emoji_canvas.winfo_width())

        emoji_frame.bind("<Configure>", on_emoji_frame_configure)
        emoji_canvas.bind("<Configure>", on_emoji_frame_configure)

        def selecionar_emoji(emoji):
            if not emoji.strip():
                messagebox.showwarning("Aviso", "O campo de ícone personalizado não pode estar vazio.")
                return
            icones_palavras_var[index].set(emoji)
            botoes_icone_refs[index].config(text=f"Ícone: {emoji}")
            seletor_window.destroy()

        row_val = 0
        col_val = 0
        for emoji in emojis_disponiveis:
            btn = tk.Button(emoji_frame, text=emoji, font=emoji_font,
                            command=lambda e=emoji: selecionar_emoji(e),
                            relief="flat", bd=0)
            btn.grid(row=row_val, column=col_val, padx=3, pady=3, sticky="nsew")
            col_val += 1
            if col_val > 5:
                col_val = 0
                row_val += 1
        
        for c in range(6):
            emoji_frame.grid_columnconfigure(c, weight=1)

        custom_icon_frame = tk.Frame(seletor_window, bg=seletor_window.cget('bg'), padx=5, pady=5)
        custom_icon_frame.grid(row=1, column=0, sticky="ew")
        custom_icon_frame.grid_columnconfigure(0, weight=1)
        custom_icon_frame.grid_columnconfigure(1, weight=2)
        custom_icon_frame.grid_columnconfigure(2, weight=1)

        tk.Label(custom_icon_frame, text="Ou digite um ícone/emoji personalizado:", font=instrucao_font, bg=seletor_window.cget('bg')).grid(row=0, column=0, sticky="w", padx=(0,5))
        
        custom_icon_var = tk.StringVar()
        custom_icon_entry = tk.Entry(custom_icon_frame, textvariable=custom_icon_var, font=entrada_font, bd=1, relief="solid", width=10)
        custom_icon_entry.grid(row=0, column=1, sticky="ew", padx=(0,5))

        tk.Button(custom_icon_frame, text="Usar Personalizado",
                  command=lambda: selecionar_emoji(custom_icon_var.get()),
                  font=botao_font, bg="#ADD8E6", fg="#333333", padx=8, pady=3, relief="raised", bd=1).grid(row=0, column=2, sticky="ew")

        nenhum_btn = tk.Button(seletor_window, text="Nenhum Ícone",
                                command=lambda: selecionar_emoji("🤔"),
                                font=botao_font, bg="#DDDDDD", padx=8, pady=3)
        nenhum_btn.grid(row=2, column=0, sticky="ew", pady=8)

        seletor_window.protocol("WM_DELETE_WINDOW", seletor_window.destroy)
        root.wait_window(seletor_window)

    for i in range(4):
        base_row = 2 + (i * 2)

        balao_label = tk.Label(content_area_frame, text="💬", font=("Segoe UI Emoji", 18), bg="white")
        balao_label.grid(row=base_row, column=0, sticky="nw", padx=(0, 3), pady=(10, 0))

        label_palavra = tk.Label(content_area_frame, text=f"Palavra {i+1}", font=label_palavra_font, bg="white", anchor="w")
        label_palavra.grid(row=base_row, column=1, sticky="w", pady=(10, 0))

        entrada_var = tk.StringVar()
        entrada = tk.Entry(content_area_frame, textvariable=entrada_var, font=entrada_font, bd=1, relief="solid", highlightbackground="#CCCCCC", highlightthickness=1)
        entrada.grid(row=base_row + 1, column=1, sticky="ew", pady=(3, 10), padx=(0, 10))
        entradas_palavras.append(entrada_var)

        icone_var = tk.StringVar(value="🤔")
        icones_palavras_var.append(icone_var)

        botao_icone = tk.Button(content_area_frame,
                                 text=f"Ícone: {icone_var.get()}",
                                 font=botao_font,
                                 bg="#E0E8F9",
                                 fg="#4A6CD2",
                                 bd=0,
                                 relief="flat",
                                 padx=8,
                                 pady=3,
                                 command=lambda idx=i: abrir_seletor_icone(idx))
        botao_icone.grid(row=base_row + 1, column=2, sticky="ew", pady=(3, 10))
        botoes_icone_refs.append(botao_icone)

    def salvar_palavras():
        dados_para_salvar = []
        for i, entrada_var in enumerate(entradas_palavras):
            palavra = entrada_var.get().strip()
            icone = icones_palavras_var[i].get()
            if not palavra:
                messagebox.showwarning("Aviso", f"A Palavra {i+1} está vazia. Por favor, preencha todas as palavras.")
                return
            dados_para_salvar.append(f"Palavra {i+1}: '{palavra}' (Ícone: {icone})")

        conteudo_txt = "\n".join(dados_para_salvar)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")],
            title="Salvar Palavras e Ícones"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(conteudo_txt)
                messagebox.showinfo("Sucesso", f"Palavras salvas com sucesso em:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao salvar o arquivo:\n{e}")
        else:
            messagebox.showinfo("Cancelado", "Operação de salvar cancelada.")


    def proximo_passo():
        palavras_para_avaliacao = []
        for i, entrada_var in enumerate(entradas_palavras):
            palavra = entrada_var.get().strip()
            icone = icones_palavras_var[i].get()
            if not palavra:
                messagebox.showwarning("Aviso", f"A Palavra {i+1} está vazia. Por favor, preença todas as palavras antes de prosseguir.")
                return
            palavras_para_avaliacao.append({'palavra': palavra, 'icone': icone})

        # Desabilita a interação com a janela principal enquanto a nova tela estiver aberta
        root.grab_set()
        AvaliacaoScreen(root, palavras_para_avaliacao)


    button_frame = tk.Frame(scrollable_frame, bg="#F0F2F5")
    button_frame.pack(pady=15)

    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)

    salvar_btn = tk.Button(button_frame, text="Salvar Palavras", command=salvar_palavras,
                            font=botao_font, bg="#4CAF50", fg="white",
                            padx=15, pady=8, relief="raised", bd=2)
    salvar_btn.grid(row=0, column=0, padx=8, pady=5)

    proximo_btn = tk.Button(button_frame, text="Próximo", command=proximo_passo,
                             font=botao_font, bg="#007BFF", fg="white",
                             padx=15, pady=8, relief="raised", bd=2)
    proximo_btn.grid(row=0, column=1, padx=8, pady=5)

    root.mainloop()

if __name__ == "__main__":
    criar_interface()
