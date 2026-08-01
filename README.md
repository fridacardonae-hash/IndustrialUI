# IndustrialUI

Desktop HMI foundation for an industrial machine with Mitsubishi PLC, Epson robot, cameras, MES and IoT connectivity.

The application starts in simulation mode by default. Configure real endpoints in `config.ini` only after the equipment and protocol details have been confirmed.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

The configuration tab is protected by the credentials defined in `config.ini` (`admin` / `change-me` by default). Change them before deployment.

## Structure

- `frontend/`: CustomTkinter HMI and configuration screens.
- `backend/`: PLC, robot-log, status and logging services.
- `config.ini`: externally editable system configuration.

## Safety note

This project is a monitoring UI foundation. It does not issue motion commands or PLC write commands. The SLMP implementation currently validates connectivity only; production register maps and interlocks must be reviewed against the actual Mitsubishi PLC program.
