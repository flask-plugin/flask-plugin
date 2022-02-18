# Plugin Config

Flask-Plugin uses Json Schema to verify the configuration. The following configurations are currently supported. Some of these options are required, and these configurations will be used by the manager to identify plugins; others are optional, and they are used to describe plugins in more detail.

## Properties

| Property   | Type                  | Required | Description                                  |
|------------|-----------------------|----------|----------------------------------------------|
| `domain`   | string                | **Yes**  | Plugin working domain.                       |
| `id`       | string                | **Yes**  | Plugin unique ID. Using for identify plugin. |
| `plugin`   | [object plugin](#plugin)     | **Yes**  | Plugin description info.                     |
| `releases` | [object releases](#releases)[] | **Yes**  | Plugin releases.                             |

## plugin

Plugin description info.

### Properties

| Property      | Type     | Required | Description               |
|---------------|----------|----------|---------------------------|
| `author`      | string   | **Yes**  | Plugin author.            |
| `name`        | string   | **Yes**  | Plugin name.              |
| `summary`     | string   | **Yes**  | A short description.      |
| `description` | string   | No       | A long description.       |
| `maintainer`  | string[] | No       | Plugin maintainers.       |
| `repo`        | string   | No       | Git repository adderss.   |
| `url`         | string   | No       | Plugin official site URL. |

## releases

Released versions.

### Properties

| Property   | Type   | Required | Description                                                              |
|------------|--------|----------|--------------------------------------------------------------------------|
| `download` | string | **Yes**  | Download zip package address.                                            |
| `version`  | string | **Yes**  | Released version number, will be parsed with python `packaging.version`. |
| `note`     | string | No       | Release note.                                                            |

