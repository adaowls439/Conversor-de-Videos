import os
import ffmpeg
from src.config import read_config
from src.log import create_log_file
from src.utils import get_video_size

def compress_and_trim_video(input_file, output_file, target_size_mb, target_last, max_attempts, scale_X, scale_Y, fps, log_file, tolerance=0.99):
    target_size_bytes = target_size_mb * 1024 * 1024
    min_size_bytes = (target_size_mb * tolerance) * 1024 * 1024
    create_log_file(log_file, f"target_size_bytes: {target_size_bytes} | min_size_bytes: {min_size_bytes}")

    # Obtem informações sobre o vídeo
    probe = ffmpeg.probe(input_file)
    duration = float(probe['format']['duration'])

    # Verifica se a duração do video é maior que a desejada
    if target_last > duration:
        create_log_file(log_file, f"ULTIMOS_SEGUNDOS ({target_last}) é maior que a duração do vídeo ({duration:.2f}). Cancelando conversão.")
        print(f"ULTIMOS_SEGUNDOS ({target_last}) é maior que a duração do vídeo ({duration:.2f}). Cancelando conversão.")
        return

    # Define o ponto de início para os últimos segundos do vídeo
    start_time = duration - target_last

    # Define a taxa de bits para atingir o tamanho alvo
    bit_rate = target_size_bytes * 8 / target_last

    # Configurações para o loop
    attempts = 0

    # Registrar início da conversão no log
    create_log_file(log_file, f"Iniciando conversão de {input_file}")
    while attempts < max_attempts:
        create_log_file(log_file, f"Tentativa {attempts + 1}")
        # Converte o vídeo
        (
            ffmpeg
            .input(input_file, ss=start_time)
            .output(output_file, **{
                'c:v': 'libx264',
                'b:v': f'{bit_rate:.0f}',
                'c:a': 'aac',
                'b:a': '128k',
                'r': f'{fps}',
                'vf': f'scale={scale_X}:{scale_Y},unsharp=5:5:1.0:5:5:0.0',
                'profile:v': 'high',
                'level:v': '4.0',
                'pix_fmt': 'yuv420p'
            })
            .run(overwrite_output=True)
        )

        # Verifica o tamanho do arquivo de saída
        output_size_bytes = get_video_size(output_file)
        diff_percent = ((output_size_bytes - target_size_bytes) / target_size_bytes)
        diff = diff_percent * 100
        if min_size_bytes <= output_size_bytes <= target_size_bytes or abs(diff) < 0.1:
            create_log_file(log_file, f"diff_percent {diff_percent*100:.2f}%")
            create_log_file(log_file, f"Sucesso! output_size_bytes {output_size_bytes}")
            break
        elif output_size_bytes > target_size_bytes:
            bit_rate *= 1 - (diff_percent * 1.1)  # Reduz a taxa de bits
            create_log_file(log_file, f"output_size_bytes {output_size_bytes} > target_size_bytes {target_size_bytes} = bit_rate - {diff:.2f}%")
        else:
            bit_rate *= 1 + (abs(diff_percent) * 1.1)  # Aumenta a taxa de bits
            create_log_file(log_file, f"output_size_bytes {output_size_bytes} < min_size_bytes {min_size_bytes} = bit_rate + {diff:.2f}%")

        attempts += 1

    if attempts == max_attempts:
        print(f"Limite de tentativas ({max_attempts}) atingido. Não foi possível alcançar o tamanho desejado.")
        create_log_file(log_file, f"Limite de tentativas ({max_attempts}) atingido. Não foi possível alcançar o tamanho desejado.")

def process_videos_in_folder(input_folder, output_folder, config_file, log_file):
    # Lê as configurações do arquivo
    config = read_config(config_file)
    target_size_mb = config.get('MB_ALVO', 7.925)
    target_last = config.get('ULTIMOS_SEGUNDOS', 30)
    max_attempts = config.get('MAX_TENTATIVAS', 10)
    scale_X = config.get('X', 1280)
    scale_Y = config.get('Y', 720)
    fps = config.get('FPS', 25)
    create_log_file(log_file, f"Configuração carregada: {config}")

    # Verifica se a pasta de entrada existe, se não, cria-a
    if not os.path.exists(input_folder):
        print(f"A pasta de entrada '{input_folder}' não existe. Criando pastas...")
        create_log_file(log_file, f"A pasta de entrada '{input_folder}' não existe. Criando pastas...")
        os.makedirs(input_folder)

        # Cria o arquivo de instruções
        with open(os.path.join(input_folder, 'Instrucoes.txt'), 'w') as f:
            f.write("Instruções de Uso:\n")
            f.write("- Organize seus vídeos na pasta 'Input';\n")
            f.write("- O script converterá e comprimirá os vídeos para a pasta 'Output';\n")
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
                compress_and_trim_video(input_file, output_file, target_size_mb, target_last, max_attempts, scale_X, scale_Y, fps, log_file)

if __name__ == '__main__':
    input_folder = './Input'
    output_folder = './Output'
    config_file = 'Config.txt'
    log_file = 'log.txt'

    create_log_file(log_file, "Iniciando conversor...")
    process_videos_in_folder(input_folder, output_folder, config_file, log_file)
