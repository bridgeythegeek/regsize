# regsize
Parses Windows Registry hive files listing the biggest key values by the size of their associated data.

## Background
The Windows Registry holds thousands upon thousands of entries, and most of them are quite small. Malware has been seen to store binaries or config files in Registry keys, for example:

- https://blog.gdatasoftware.com/blog/article/poweliks-the-persistent-malware-without-a-file.html
- http://vrt-blog.snort.org/2014/09/malware-using-registry-to-store-zeus.html

By listing the Registry key values by their size, or at least the top 20, an investigator can quickly identify keys that have an abnormally large size.
## Requirements
### python-registry
The fantastic python-registry module which does all the heavy lifting of parsing the registry files.
- http://www.williballenthin.com/registry/

## Usage
```
usage: regsize.py [-h] [--max MAX] [--no-ent] [--csv] target [target ...]

positional arguments:
  target             file to analyse. supports globbing: folder/*

optional arguments:
  -h, --help         show this help message and exit
  --max MAX, -m MAX  report the top MAX sizes
  --no-ent, -E       don't calculate the Shannon entropy
  --csv              output as csv
```
## Usage Examples
```
regsize.py --max=5 reg/SYSTEM reg/SOFTWARE
regsize.py reg/* /some/other/folder/NTUSER.DAT
```
## A note on 'max'
The 'max' setting does not limit the number of key values returned, but the number of unique sizes. This is deliberate.

For example, with <tt>--max=3</tt> you might get more than 3 keys returned. For example:
```
$ python3 regsize.py --max=3 /media/user/WINDOWS/Windows/System32/config/DEFAULT
[/media/user/WINDOWS/Windows/System32/config/DEFAULT]
32768     Software\SSPrint\spe__\UPDEScripts
26360     Software\SSPrint\spe__\Samsung Universal Print Driver 2\Capabilities
8008      Software\SSPrint\spe__\Samsung Universal Print Driver 2\ScratchData\DevMode_spem_
8008      Software\SSPrint\spe__\Samsung Universal Print Driver 2\DefaultData\DevMode_spem_
```
If regsize had truncated at 3, you would only see one of the bottom two entries. This would've been misleading.
## A note on Shannon entropy
In short, Shannon entropy is a measure of entropy which scores between 0 and 8. The closer to 8, the greater the entropy in the data.
This can be useful for finding binaries or encrypted data.
## Real-life Example
```
$ python regsize.py --max=5 --no-ent /media/user/SHARED/reg/NTUSER.DAT 
[/media/user/SHARED/reg/NTUSER.DAT]
153484    Software\Microsoft\Windows\CurrentVersion\Explorer\StartPage2\ProgramsCache
123592    Software\ksrfmu\pawd
55362     Software\Microsoft\Windows\CurrentVersion\Explorer\PhotoPrintingWizard\--REDACTED--\--REDACTED--\PrintCapabilites
18820     Software\Microsoft\Windows\CurrentVersion\Explorer\PhotoPrintingWizard\--REDACTED--\--REDACTED--\PrintTicket
9547      Software\Microsoft\Windows\CurrentVersion\Internet Settings\4
```
In this instance, <tt>pawd</tt> contained an encoded binary. The Shannon entropy is not shown because the <tt>--no-ent</tt> switch was used.
```
$ python regsize.py --max=6 /tmp/win/Windows/System32/config/SYSTEM
[/tmp/win/Windows/System32/config/SYSTEM]
92160  0.05285 CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}\ControlSet001\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000\MMDMMContext
71278  3.78619 CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}\ControlSet001\Control\Session Manager\AppCompatCache\AppCompatCache
68039  7.78358 CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}\ControlSet001\Services\rdyboost\Parameters\BootPlan
23700  3.39098 CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}\ControlSet001\Control\ProductOptions\ProductPolicy
21200  0.01283 CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}\ControlSet001\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000\ModePersistence
11784  1.40188 CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}\ControlSet001\Enum\ACPI_HAL\PNP0C08\0\LogConf\BasicConfigVector
```
In this example, the Shannon entropy of each data can be seen in the second column.
### As an aside...
In the first real-life example, <tt>ProgramsCache</tt> was full of <tt>0x00</tt>. Still haven't been able to figure out why. Do please let me know if you know of a reason why this might be so!
