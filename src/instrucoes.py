import os

def create_instructions_file():
    instructions_file_path = os.path.join(os.getcwd(), 'Instrucoes.txt')
    with open(instructions_file_path, 'w') as f:
        f.write("Instruções de Uso:\n")
        f.write("- Organize seus vídeos na pasta 'Input';\n")
        f.write("- O script converterá e comprimirá os vídeos para a pasta 'Output';\n")
        f.write("- Altere as configurações em Config.txt;\n")
        f.write("- O arquivo pode ser convertido varias vezes até chegar ao tamanho desejado;\n")
        f.write("- Certifique-se de que os arquivos de vídeo sejam no formato .mp4.\n")
