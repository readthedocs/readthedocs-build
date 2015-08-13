from .builder import builder_types


def build(project_config):
    for build_config in project_config:
        builder_type = build_config['type']
        builder_class = builder_types[builder_type]
        builder = builder_class(
            build_config=build_config)
        builder.build()
