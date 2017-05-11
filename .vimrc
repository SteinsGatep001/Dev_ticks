" ----------------------- Vundle 插件管理 ---------------- 
set nocompatible              " be iMproved, required
filetype off                  " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'

" The following are examples of different formats supported.
" Keep Plugin commands between vundle#begin/end.
" plugin on GitHub repo
Plugin 'tpope/vim-fugitive'
" plugin from http://vim-scripts.org/vim/scripts.html
Plugin 'L9'
" The sparkup vim script is in a subdirectory of this repo called vim.
" Pass the path to set the runtimepath properly.
Plugin 'rstacruz/sparkup', {'rtp': 'vim/'}

" ------------------- mine plugin ------------------------------------
" Python 自动补全
Bundle 'Valloric/YouCompleteMe'
" Python 缩进插件
Plugin 'vim-scripts/indentpython.vim'
" jedi python
Bundle 'davidhalter/jedi-vim' 
" 树形浏览文件
Plugin 'scrooloose/nerdtree'
" 拓展TAB键
Plugin 'jistr/vim-nerdtree-tabs'
" c++ 增强型高亮
Plugin 'octol/vim-cpp-enhanced-highlight'
" 将相同缩进的代码标示
Plugin 'nathanaelkane/vim-indent-guides'


" All of your Plugins must be added before the following line
call vundle#end()            " required
filetype plugin indent on    " required
" To ignore plugin indent changes, instead use:
"filetype plugin on
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal


" -------------------插件相关配置-----------------------------
"  ++++++++++++++++++ YCM ++++++++++++++++++++++++
" 保证自动补全窗口不消失
let g:ycm_autoclose_preview_window_after_completion=1
" 语法关键字补全
let g:ycm_seed_identifiers_with_syntax=1
" 从键入第1个字符就显示匹配项
let g:ycm_min_num_of_chars_for_completion=1
" 允许加载ycm_extra_conf
let g:ycm_confirm_extra_conf=0
" ++++++++++++++++++ 语法补全插件 ++++++++++++++++++
" clang需要安装sudo apt-get install cmake libblkid-dev e2fslibs-dev libboost-all-dev libaudit-dev
" 然后http://llvm.org/releases/download.html 下载编译
" python 直接jedi

" ++++++++++++++++++++ vim-indent-guide +++++++++++++++++++++++
" 随 vim 自启动
let g:indent_guides_enable_on_vim_startup=1
" 从第二层开始可见
let g:indent_guides_start_level=2
" 设置字块宽度
let g:indent_guides_guide_size=1


" vim 启动默认开启树形文件浏览
autocmd VimEnter * NERDTree


" --------------------- 个人基本设置 ---------------------------
" 使用主题
colorscheme monokai
"colorscheme molokai
" 设置行标
set number
" 设置折叠
set foldmethod=indent
set foldlevel=99
" 设置空格折叠快捷键
nnoremap <space> za
" 开启语法高亮
syntax on
" 允许指定语法高亮方案替换默认的高亮方案
syntax on
" 自动适应不同语言的缩进
filetype indent on
" 制表符转换为空格
set expandtab
" 设置编辑时制表符占空格数
set tabstop=4
" 设置格式化时制表符占空格数
set shiftwidth=4
" 设置nerdtree窗口大小
let g:NERDTreeWinSize = 15

