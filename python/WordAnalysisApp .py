import os
import json
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

# Caminhos
CURRENT_DIR = os.path.dirname(__file__)
ARQUIVO_PALAVRAS = os.path.join(CURRENT_DIR, "palavras.json")


class IconeExibidorApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        with layout.canvas.before:
            Color(0.9, 0.85, 1, 1) # Azul muito claro (RGBA)
            fundo = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
       #background_color=(0.1, 0.4, 0.8, 1), 
        layout.bind(size=lambda inst, val: setattr(fundo, 'size', val))
        layout.bind(pos=lambda inst, val: setattr(fundo, 'pos', val))


        btn_exibir = Button(
            text="Mostrar Palavra e Ícone",
            background_color=(0.1, 0.4, 0.8, 1), 
            size_hint=(1, None),
            height=dp(50)
        )
        btn_exibir.bind(on_release=self.mostrar_popup)

        layout.add_widget(btn_exibir)
        return layout

    def mostrar_popup(self, instance):
        if not os.path.exists(ARQUIVO_PALAVRAS):
            self.popup_alerta("Arquivo não encontrado", "Nenhum arquivo de palavras foi encontrado.")
            return

        try:
            with open(ARQUIVO_PALAVRAS, "r", encoding="utf-8") as f:
                dados = json.load(f)

            if not dados:
                self.popup_alerta("Lista vazia", "O arquivo está vazio.")
                return

            entrada = dados[0]
            palavra = entrada.get("palavra", "Sem Palavra")
            caminho_icone = entrada.get("icone", "")

            content = BoxLayout(orientation='vertical', spacing=10, padding=20)

            # Cor personalizada do fundo da janela
            with content.canvas.before:
                fundo = RoundedRectangle(size=content.size, pos=content.pos, radius=[15])
                content.bind(size=lambda inst, val: setattr(fundo, 'size', val))
                content.bind(pos=lambda inst, val: setattr(fundo, 'pos', val))

            # Ícone como imagem
            if caminho_icone and os.path.exists(caminho_icone):
                imagem = Image(source=caminho_icone, size_hint_y=None, height=150)
                content.add_widget(imagem)
            else:
                erro_icon = Label(text="[Ícone não encontrado]", color=(1, 0, 0, 1), font_size=16)
                content.add_widget(erro_icon)

            # Palavra abaixo do ícone
            content.add_widget(Label(
                text=palavra,
                font_size=32,
                #color=(0, 0, 0, 1),
               # background_color=(0.8, 0.9, 1, 1),
                size_hint_y=None,
                height=40,
                halign='center'
            ))

            # Botão de fechar
            btn_fechar = Button(
                text="Fechar", 
                size_hint_y=None, 
                font_size=32,
                height=dp(40), 
                color=(1, 1, 1, 1),
                background_normal="",
                background_color=(0.1, 0.6, 0.9, 1,
                
                ) 
                )
            
            popup = Popup(title="Palavra e Ícone", 
                          content=content,
                          size_hint=(0.7, 0.5)
                          )
            btn_fechar.bind(on_release=popup.dismiss)
            content.add_widget(btn_fechar)
            popup.open()

        except Exception as e:
            self.popup_alerta("Erro", f"Ocorreu um erro ao abrir o arquivo:\n{e}")

    def popup_alerta(self, titulo, mensagem):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        with layout.canvas.before:
            Color(1, 0.95, 0.95, 1)  # Fundo claro rosado
            bg = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[15])
        layout.bind(size=lambda inst, val: setattr(bg, 'size', val))
        layout.bind(pos=lambda inst, val: setattr(bg, 'pos', val))

        aviso = Label(text=mensagem, color=(0, 0, 0, 1), font_size=16)
        btn_ok = Button(text="OK", size_hint_y=None, height=dp(40))
        popup = Popup(title=titulo, content=layout, size_hint=(0.6, 0.3))
        btn_ok.bind(on_release=popup.dismiss)

        layout.add_widget(aviso)
        layout.add_widget(btn_ok)
        popup.open()


if __name__ == '__main__':
    IconeExibidorApp().run()
