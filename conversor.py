import os
import ffmpeg

def get_video_size(file_path):
    return os.path.getsize(file_path)

def read_config(config_file):
    default_config = {
        'MB_ALVO': 7.925,
        'ULTIMOS_SEGUNDOS': 30
    }

    # Verifica se o arquivo de configuração existe
    if not os.path.exists(config_file):
        # Cria o arquivo de configuração com os valores padrão
        with open(config_file, 'w') as f:
            for key, value in default_config.items():
                f.write(f"{key} = {value}\n")

    # Lê as configurações do arquivo
    config = {}
    with open(config_file, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.split('=')
                config[key.strip()] = float(value.strip())

    return config

def compress_and_trim_video(input_file, output_file, target_size_mb, target_last, tolerance=0.05):
    target_size_bytes = target_size_mb * 1024 * 1024
    min_size_bytes = (target_size_mb - tolerance) * 1024 * 1024
    max_size_bytes = (target_size_mb + tolerance) * 1024 * 1024

    # Obtem informações sobre o vídeo
    probe = ffmpeg.probe(input_file)
    duration = float(probe['format']['duration'])

    # Definane o ponto de início para os últimos segundos do vídeo
    start_time = duration - target_last

    # Define a taxa de bits para atingir o tamanho alvo
    bit_rate = target_size_bytes * 8 / target_last

    while True:
        # Converte o vídeo
        (
            ffmpeg
            .input(input_file, ss=start_time)
            .output(output_file, **{
                'c:v': 'libx264',
                'b:v': f'{bit_rate:.0f}',
                'c:a': 'aac',
                'b:a': '128k',
                'r': 25,
                'vf': 'scale=1280:720,unsharp=5:5:1.0:5:5:0.0',
                'profile:v': 'high',
                'level:v': '4.0',
                'pix_fmt': 'yuv420p'
            })
            .run(overwrite_output=True)
        )

        # Verifica o tamanho do arquivo de saída
        output_size_bytes = get_video_size(output_file)

        if min_size_bytes <= output_size_bytes <= max_size_bytes:
            break
        elif output_size_bytes > max_size_bytes:
            bit_rate *= 0.9  # Reduz a taxa de bits em 10%
        else:
            bit_rate *= 1.1  # Aumenta a taxa de bits em 10%

def process_videos_in_folder(input_folder, output_folder, config_file):
    # Lê as configurações do arquivo
    config = read_config(config_file)
    target_size_mb = config.get('MB_ALVO', 7.925)
    target_last = config.get('ULTIMOS_SEGUNDOS', 30)

    # Verifica se a pasta de entrada existe, se não, cria-a
    if not os.path.exists(input_folder):
        print(f"A pasta de entrada '{input_folder}' não existe. Criando pasta...")
        os.makedirs(input_folder)

        # Cria o arquivo de instruções
        with open(('Instrucoes.txt'), 'w') as f:
            f.write("Instruções de Uso:\n")
            f.write("- Organize seus vídeos na pasta 'Input';\n")
            f.write("- O script converterá e comprimirá os vídeos para 720p na pasta 'Output';\n")
            f.write("- Altere as configurações em Config.txt;\n")
            f.write("- O arquivo pode ser convertido varias vezes até chegar ao tamanho desejado;\n")
            f.write("- Certifique-se de que os arquivos de vídeo sejam no formato .mp4.\n")

    # Verifica se a pasta de saída existe, se não, cria-a
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Itera pelos arquivos na pasta de entrada
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".mp4"):  # Verifica se é um arquivo de vídeo
                input_file = os.path.join(root, file)
                
                # Nome do arquivo de saída com "convertido" no final
                output_file = os.path.join(output_folder, f"{os.path.splitext(file)[0]}_Convertido.mp4")
                
                # Chama a função para converter e comprimir o vídeo
                compress_and_trim_video(input_file, output_file, target_size_mb, target_last)

input_folder = './Input'
output_folder = './Output'
config_file = 'Config.txt'

process_videos_in_folder(input_folder, output_folder, config_file)
