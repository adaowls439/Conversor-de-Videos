import ffmpeg
from src.log import create_log_file
from src.utils import get_video_size

# Comprime e corta o video
def compress_and_trim_video(target_size_bytes, cut_duration, input_file, max_attempts, start_time, end_time, output_file, fps, scale_X, scale_Y, min_size_bytes):
    # Define a taxa de bits para atingir o tamanho alvo
    bit_rate = target_size_bytes * 8 / cut_duration

    # Configurações para o loop
    attempts = 0

    # Registrar início da conversão no log
    create_log_file(f"Iniciando conversão de {input_file}")

    while attempts < max_attempts:
        create_log_file(f"Tentativa {attempts + 1}")
        # Converte o vídeo
        (
            ffmpeg
            .input(input_file, ss=start_time, to=end_time)
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
            create_log_file( f"diff_percent {diff_percent*100:.2f}%")
            create_log_file(f"Sucesso! output_size_bytes {output_size_bytes}")
            break
        elif output_size_bytes > target_size_bytes:
            bit_rate *= 1 - (diff_percent * 1.1)  # Reduz a taxa de bits
            create_log_file( f"output_size_bytes {output_size_bytes} > target_size_bytes {target_size_bytes} = bit_rate - {diff:.2f}%")
        else:
            bit_rate *= 1 + (abs(diff_percent) * 1.1)  # Aumenta a taxa de bits
            create_log_file(f"output_size_bytes {output_size_bytes} < min_size_bytes {min_size_bytes} = bit_rate + {diff:.2f}%")

        attempts += 1

    if attempts == max_attempts:
        print(f"Limite de tentativas ({max_attempts}) atingido. Não foi possível alcançar o tamanho desejado.")
        create_log_file(f"Limite de tentativas ({max_attempts}) atingido. Não foi possível alcançar o tamanho desejado.")

def cut_video(input_file, output_file, start_time, end_time):
    # Registrar início do corte no log
    create_log_file(f"Iniciando corte de {input_file}")

    try:
        # Realiza o corte do vídeo
        (
            ffmpeg
            .input(input_file, ss=start_time, to=end_time)
            .output(output_file, c='copy')
            .run(overwrite_output=True)
        )

        create_log_file( f"Corte realizado com sucesso: {input_file} -> {output_file}")

    except ffmpeg.Error as e:
        create_log_file( f"Erro ao cortar o vídeo: {e.stderr.decode('utf8')}")
        print(f"Erro ao cortar o vídeo: {e.stderr.decode('utf8')}")