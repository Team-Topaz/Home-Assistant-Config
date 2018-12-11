# Note
Borrowed this prefix information from [Apocrathia's Home Assistant Configuration](https://github.com/Apocrathia/home-assistant-config). They don't list a license in their config, so hopefully they're chill with this.

# Packages

In order to keep my configuration organized and easy to work with, I have opted
to use Home Assistant's
[Packages](https://www.home-assistant.io/docs/configuration/packages/)
functionality. This allows me to keep all of my code pertaining to something
together.

## Naming Convention

Because the ```package: !include_dir_named``` statement does not recursively
search a direcctory, all of the relegant configuration files must be within
that folder. To make my files organized, I have have prefixed them with a
function idenfier. That way they are grouped together in a logical manner.

Prefix | Description | Example
--- | --- | ---
platform | Everything to set up and configure a specific platform. | platform_nest
routine | A collection of configurations to perform tasks which happen on a daily basis | routine_morning
function | Specific functions that can be bundled together | function_presence
system | Things that work specifically with  the management of Home Assistant | system_backup
toy | Things that have no real use, but are just for fun. | toy_annoyaimee
mode | Contains features that change the way the automation system behaves. | mode_homealone
components | Logical groupings of a specific type of component (or similar) | components_lighting
