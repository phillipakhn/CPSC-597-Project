# Frontend/utils/pcap_converter.py
import shutil

# Check if cicflowmeter exists

def cicflowmeter_available():
    return shutil.which("cicflowmeter") is not None

# Detect PCAP files

def is_pcap_filename(filename: str) -> bool:
    filename = filename.lower()
    return filename.endswith((".pcap", ".pcapng", ".pcap_iscx"))


# Convert PCAP to CSV

def convert_uploaded_pcap_to_csv(
    uploaded_file,
    original_filename=None,
    project_root=None,
    keep_csv=True,
):
    from pathlib import Path
    import tempfile
    import shutil
    import subprocess
    
    # Temp directory
    
    temp_dir = tempfile.mkdtemp()

    filename = original_filename or uploaded_file.name
    pcap_path = Path(temp_dir) / filename

    with open(pcap_path, "wb") as f:
        f.write(uploaded_file.read())

    output_csv = Path(temp_dir) / (pcap_path.stem + ".csv")

    
    # Save location (portable)
    
    if project_root:
        save_dir = Path(project_root) / "generated_csv"
    else:
        save_dir = Path("generated_csv")

    save_dir.mkdir(exist_ok=True)
    saved_csv = save_dir / (pcap_path.stem + ".csv")
    
    # Run cicflowmeter
    
    cicflowmeter_cmd = Path(project_root) / "cicflowmeter" / ".venv" / "bin" / "cicflowmeter"

    cmd = [
        str(cicflowmeter_cmd),
        "-f", str(pcap_path),
        "-c",
        str(output_csv),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "PCAP conversion failed.\n\n"
            f"Command: {' '.join(cmd)}\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )

    if not output_csv.exists():
        raise RuntimeError("Conversion finished but CSV was not created.")

    
    # Save copy if requested
    
    if keep_csv:
        shutil.copy(output_csv, saved_csv)

    return str(output_csv), str(saved_csv)