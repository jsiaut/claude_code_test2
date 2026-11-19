! C2 : un builtin de GCC appelé par bind(c) reste un symbole externe (aucun mécanisme d'import d'intrinsèques).
program fb
  interface
    subroutine pause() bind(c, name='__builtin_ia32_pause')
    end subroutine
  end interface
  call pause()
end program
