# regsize
Parses Windows Registry hive files listing the biggest key values by the size of their associated data.

## Background
The Windows Registry holds thousands upon thousands of entries, and most of them are quite small. Malware has been seen to store binaries or config files in Registry keys, for example:

- https://blog.gdatasoftware.com/blog/article/poweliks-the-persistent-malware-without-a-file.html
- http://vrt-blog.snort.org/2014/09/malware-using-registry-to-store-zeus.html

By listing the Registry key values by their size, or at least the top 10, an investigator can quickly identify keys that have an abnormally large size.
## Requirements
### Python3
The script has been written to run in  python3.
### python-registry
The fantastic python-registry module which does all the heavy lifting of parsing the registry files.
- http://www.williballenthin.com/registry/

## Usage
```
usage: regsize.py [-h] [--max MAX] target [target ...]

positional arguments:
  target             file to analyse. supports globbing: folder/*

optional arguments:
  -h, --help         show this help message and exit
  --max MAX, -m MAX  report the top MAX sizes
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
## Real-life Example
```
$ python3 regsize.py --max=5 /media/user/SHARED/reg/NTUSER.DAT 
[/media/user/SHARED/reg/NTUSER.DAT]
153484    Software\Microsoft\Windows\CurrentVersion\Explorer\StartPage2\ProgramsCache
123592    Software\ksrfmu\pawd
55362     Software\Microsoft\Windows\CurrentVersion\Explorer\PhotoPrintingWizard\--REDACTED--\--REDACTED--\PrintCapabilites
18820     Software\Microsoft\Windows\CurrentVersion\Explorer\PhotoPrintingWizard\--REDACTED--\--REDACTED--\PrintTicket
9547      Software\Microsoft\Windows\CurrentVersion\Internet Settings\4
```
In this instance, <tt>pawd</tt> contained an encoded binary.
### As an aside...
In this real-life example, <tt>ProgramsCache</tt> was full of <tt>0x00</tt>. Still haven't been able to figure out why. Do please let me know if you know of a reason why this might be so!
