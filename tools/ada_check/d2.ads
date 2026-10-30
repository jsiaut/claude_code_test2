with Interfaces; use Interfaces;
package D2 is
   C_Seq : Integer_64 := 0 with Atomic;
   C_Rel : Integer_64 := 0 with Atomic;
   pragma Disable_Atomic_Synchronization (C_Rel);
   procedure Store_Seq (V : Integer_64);
   procedure Store_Rel (V : Integer_64);
   function Load_Rel return Integer_64;
end D2;
