local s = string.pack("<f", 1.0)
print(string.format("CAP;A5;0.5;string.pack/unpack : 0x%08x", string.unpack("<I4", s)))
print("CAP;F3;0.5;entiers 64 bits enveloppants : " .. tostring(math.maxinteger + 1 == math.mininteger) .. " ; math.ult " .. tostring(math.ult(1, -1)))
