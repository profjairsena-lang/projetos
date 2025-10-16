from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

def abrir_janela_colorida():
    layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

    with layout.canvas.before:
        Color(0.95, 0.85, 0.9, 1)  # Cor de fundo rosa claro (RGBA)
        fundo = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[15])

    layout.bind(size=lambda inst, val: setattr(fundo, 'size', val))
    layout.bind(pos=lambda inst, val: setattr(fundo, 'pos', val))

    mensagem = Label(text="Fundo colorido aplicado!", font_size=20, color=(0, 0, 0, 1))
    botao_fechar = Button(text="Fechar", size_hint_y=None, height=dp(40))
    
    popup = Popup(title="Janela Colorida", content=layout, size_hint=(0.7, 0.5))
    botao_fechar.bind(on_release=popup.dismiss)

    layout.add_widget(mensagem)
    layout.add_widget(botao_fechar)

    popup.open()
