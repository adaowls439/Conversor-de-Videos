import os
import ffmpeg
from src.config import read_config
from src.log import create_log_file
from src.utils import get_video_size
from src.instrucoes import create_instructions_file
from src.comprime_e_corta import compress_and_trim_video, cut_video

def preprocess_video_action(input_file, output_file, target_size_mb, cut_start, cut_end, max_attempts, scale_X, scale_Y, fps, tolerance=0.99):
    # Obtem informações sobre o vídeo original
    original_size_bytes = os.path.getsize(input_file)
    original_size_mb = original_size_bytes / (1024 * 1024)

    # Obtem informações sobre o vídeo
    probe = ffmpeg.probe(input_file)
    duration = float(probe['format']['duration'])

    # Verifica o FPS original do vídeo
    original_fps = eval(probe['streams'][0]['r_frame_rate'])  # 'r_frame_rate' is in the format 'numerator/denominator'

    # Usa o FPS original se o FPS desejado for maior que o original
    if fps > original_fps:
        create_log_file(f"O FPS desejado ({fps}) é maior que o FPS original ({original_fps}). Usando FPS original.")
        fps = original_fps

    # Calcula o ponto de início e duração do vídeo após o corte
    cut_duration = duration - cut_start - cut_end

    start_time = cut_start
    end_time = cut_start + cut_duration

    # Verifica se o tamanho alvo é menor ou igual ao tamanho do arquivo original
    if target_size_mb > 0 and target_size_mb <= original_size_mb:
        target_size_bytes = target_size_mb * 1024 * 1024
        min_size_bytes = (target_size_mb * tolerance) * 1024 * 1024
        create_log_file(f"target_size_bytes: {target_size_bytes} | min_size_bytes: {min_size_bytes}")

        # Verifica se a duração do vídeo após o corte é suficiente
        if cut_duration <= 3:
            create_log_file(f"O vídeo após o corte tem duração não válida ({cut_duration:.2f} segundos). Cancelando conversão.")
            print(f"O vídeo após o corte tem duração não válida ({cut_duration:.2f} segundos). Cancelando conversão.")
            return

        # Comprime e corta o video
        compress_and_trim_video(target_size_bytes, cut_duration, input_file, max_attempts, start_time, end_time, output_file, fps, scale_X, scale_Y, min_size_bytes)

    else:
        create_log_file(f"Erro: O tamanho alvo ({target_size_mb} MB) é maior que o tamanho do arquivo original ({original_size_mb:.2f} MB). Não é necessário converter.")
        print(f"Erro: O tamanho alvo ({target_size_mb} MB) é maior que o tamanho do arquivo original ({original_size_mb:.2f} MB). Não é necessário converter.")

        cut_video(input_file, output_file, start_time, end_time)
        return

def process_videos_in_folder(input_folder, output_folder, config_file):
    # Lê as configurações do arquivo
    config = read_config(config_file)
    target_size_mb = config.get('MB_ALVO', 7.925)
    cut_start = config.get('CORTAR_INICIO', 0)
    cut_end = config.get('CORTAR_FIM', 0)
    max_attempts = config.get('MAX_TENTATIVAS', 10)
    scale_X = config.get('X', 1280)
    scale_Y = config.get('Y', 720)
    fps = config.get('FPS', 25)
    create_log_file(f"Configuração carregada: {config}")

    # Verifica se a pasta de entrada existe, se não, cria-a
    if not os.path.exists(input_folder):
        print(f"A pasta de entrada '{input_folder}' não existe. Criando pastas...")
        create_log_file(f"A pasta de entrada '{input_folder}' não existe. Criando pastas...")
        os.makedirs(input_folder)

        # Cria o arquivo de instruções
        create_instructions_file()

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
                preprocess_video_action(input_file, output_file, target_size_mb, cut_start, cut_end, max_attempts, scale_X, scale_Y, fps)

if __name__ == '__main__':
    input_folder = './Input'
    output_folder = './Output'
    config_file = 'Config.txt'

    create_log_file("Iniciando conversor...")
    process_videos_in_folder(input_folder, output_folder, config_file)
