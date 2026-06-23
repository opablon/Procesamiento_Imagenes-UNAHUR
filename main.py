from multiprocessing import freeze_support


def main() -> None:
    from gui.ventana_principal import iniciar_aplicacion

    iniciar_aplicacion()

if __name__ == "__main__":
    print("Iniciando aplicación...")  # Esto aparecerá en la terminal
    freeze_support()
    main()
