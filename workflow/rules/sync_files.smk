
rule parla_clarin_sync_text:
    run:
        utility.sync_delta_names(
            config['parla_clarin']['source_folder'], "xml", config['target_export_folder'], "txt", delete=True
        )
