module tm
  implicit none
  template gsum_t(T)
    type, deferred :: T
  end template
end module
