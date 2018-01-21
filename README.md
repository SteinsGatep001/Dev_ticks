# Dev_ticks
Something of develop

## extract

```bash
tar xvzf file.tar.gz - tgfo uncompress a gzip tar file (.tgz or .tar.gz)
tar xvjf file.tar.bz2 - to uncompress a bzip2 tar file (.tbz or .tar.bz2) to extract the contents.
tar xvf file.tar - to uncompressed tar file (.tar)
tar xvC /var/tmp -f file.tar - to uncompress tar file (.tar) to another directory
# xz
tar xf archive.tar.xz
tar xf archive.tar.gz
tar xf archive.tar
```

## something about ubuntu
some about ubuntu config

### encode error

##### error
```bash
perl: warning: Setting locale failed.
perl: warning: Please check that your locale settings:
	LANGUAGE = (unset),
	LC_ALL = (unset),
	LC_CTYPE = "zh_CN.UTF-8",
	LANG = "en_US.UTF-8"
```
#### solution1
1. generate locale
```
locale-gen en_US.UTF-8
```
2. locale settings
```bash
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
locale-gen en_US.UTF-8
dpkg-reconfigure locales
```

#### solution2
edit `/etc/environment`
```bash
LC_ALL=en_US.UTF-8
LANG=en_US.UTF-8
```
