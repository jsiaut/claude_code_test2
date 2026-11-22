# Régions des formes (v4, point 5)

*Écrit par `tools/cost/count.py` à partir du relevé `tools/cost/regions.py` ; plan : `docs/V4_COST.md`, 3.2. Intervalles de lignes (bornes comprises) dans les copies `bench/<langage>_cv`.*

## c

* `k1|natural|energy` (entrée `k1_natural`) : k1_natural ms.c:138-143 — L 6, T 97, U 0, X 0
* `k1|soa|energy` (entrée `k1_soa`) : k1_soa ms.c:157-174 ; k1_soa_prep ms.c:203-208 — L 24, T 368, U 0, X 10
* `k3|sw_packed|` (entrée `k3_worker`) : k3 ms.c:256-266, ms.c:268-270, ms.c:275-276, ms.c:278-279 — L 18, T 245, U 0, X 0
* `k3|sw_padded|` (entrée `k3_worker`) : k3 ms.c:256-266, ms.c:268-270, ms.c:275-276, ms.c:278-279 — L 18, T 245, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4_natural`) : k4_natural ms.c:290-295 — L 6, T 58, U 0, X 0
* `k4|tuned|` (entrée `k4_tuned`) : k4_tuned ms.c:304-317 — L 14, T 139, U 0, X 6
* `k5|natural|` (entrée `k5_natural`) : k5_natural ms.c:363-367 — L 5, T 59, U 0, X 0
* `k5|tuned|` (entrée `k5_tuned`) : k5_tuned ms.c:368-377 — L 10, T 180, U 0, X 6
* `k6|mt_pool_v|q6` (entrée `k6_job`) : pool ms.c:82-117 ; k6_job ms.c:504-510 ; k6_pool_run ms.c:517-517, ms.c:525-532, ms.c:558-558 ; q6_tuned_v ms.c:478-494 ; q6_natural ms.c:401-407 — L 77, T 963, U 0, X 12
* `k6|mt_pool|q1` (entrée `k6_job`) : pool ms.c:82-117 ; k6_job ms.c:504-510 ; k6_pool_run ms.c:517-517, ms.c:525-532, ms.c:558-558 ; q1_tuned ms.c:434-473 ; q1_natural ms.c:418-430 — L 106, T 1450, U 0, X 24
* `k6|mt|q1` (entrée `k6_worker`) : k6_worker ms.c:495-501 ; k6_mt_run ms.c:534-545 ; q1_tuned ms.c:434-473 ; q1_natural ms.c:418-430 — L 72, T 1181, U 0, X 24
* `k6|natural|q1` (entrée `q1_natural`) : q1_natural ms.c:418-430 — L 13, T 176, U 0, X 0
* `k6|natural|q6` (entrée `q6_natural`) : q6_natural ms.c:401-407 — L 7, T 111, U 0, X 0
* `k6|tuned_v|q6` (entrée `q6_tuned_v`) : q6_tuned_v ms.c:478-494 ; q6_natural ms.c:401-407 — L 24, T 376, U 0, X 12
* `k6|tuned|q1` (entrée `q1_tuned`) : q1_tuned ms.c:434-473 ; q1_natural ms.c:418-430 — L 53, T 863, U 0, X 24
* `k7|natural|` (entrée `Node7`) : k7_natural ms.c:564-564, ms.c:577-577, ms.c:579-587 — L 11, T 158, U 0, X 0
* `k7|tuned|` (entrée `Slot7`) : k7_tuned ms.c:565-565, ms.c:593-593, ms.c:595-610 — L 18, T 235, U 0, X 0
* `k8|natural|` (entrée `t8_build`) : k8_natural ms.c:622-631 — L 10, T 169, U 0, X 0
* `k8|tuned_it|` (entrée `a8i_build`) : k8_tuned_it ms.c:633-633, ms.c:660-695, ms.c:707-707 — L 38, T 350, U 0, X 0
* `k9|mt_pool_v|` (entrée `k9_job`) : pool ms.c:82-117 ; k9_job ms.c:774-780 ; k9_pool_run ms.c:787-787, ms.c:797-797, ms.c:815-815 ; k9_rows_v ms.c:757-771 — L 61, T 692, U 0, X 5
* `k9|mt_pool|` (entrée `k9_job`) : pool ms.c:82-117 ; k9_job ms.c:774-780 ; k9_pool_run ms.c:787-787, ms.c:797-797, ms.c:815-815 ; k9_rows ms.c:746-752 — L 53, T 611, U 0, X 0
* `k9|natural|` (entrée `k9_natural`) : k9_natural ms.c:741-745 — L 5, T 118, U 0, X 0
* `k9|tuned_v|` (entrée `k9_rows_v`) : k9_rows_v ms.c:757-771 — L 15, T 242, U 0, X 5

## odin

* `k1|natural|energy` (entrée `k1_natural`) : k1_natural ms.odin:42-46 — L 5, T 61, U 0, X 0
* `k1|soa|energy` (entrée `k1_soa`) : k1_soa ms.odin:61-80 ; k1_soa_prep ms.odin:110-112 — L 23, T 348, U 20, X 0
* `k3|sw_packed|` (entrée `k3_worker`) : k3 ms.odin:155-167, ms.odin:169-170, ms.odin:172-173, ms.odin:175-177, ms.odin:179-179, ms.odin:181-183 — L 24, T 221, U 0, X 0
* `k3|sw_padded|` (entrée `k3_worker`) : k3 ms.odin:155-167, ms.odin:169-170, ms.odin:172-173, ms.odin:175-177, ms.odin:179-179, ms.odin:181-183 — L 24, T 221, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4_natural`) : k4_natural ms.odin:230-234 — L 5, T 35, U 0, X 0
* `k4|tuned|` (entrée `k4_tuned`) : k4_tuned ms.odin:243-262 — L 20, T 177, U 0, X 0
* `k5|natural|` (entrée `k5_natural`) : k5_natural ms.odin:304-308 — L 5, T 42, U 0, X 0
* `k5|tuned|` (entrée `k5_tuned`) : k5_tuned ms.odin:309-319 — L 11, T 209, U 11, X 0
* `k6|mt_pool_v|q1` (entrée `k6_pool_job`) : pool ms.odin:196-227 ; k6_pool ms.odin:474-487 ; k6_pool_run ms.odin:492-492, ms.odin:498-500, ms.odin:521-521 ; q1_tuned_v ms.odin:421-457 — L 88, T 954, U 41, X 0
* `k6|mt_pool|q6` (entrée `k6_pool_job`) : pool ms.odin:196-227 ; k6_pool ms.odin:474-487 ; k6_pool_run ms.odin:492-492, ms.odin:498-500, ms.odin:521-521 ; q6_tuned ms.odin:352-366 — L 66, T 654, U 19, X 0
* `k6|natural|q1` (entrée `q1_natural`) : q1_natural ms.odin:367-380 — L 14, T 153, U 0, X 0
* `k6|natural|q6` (entrée `q6_natural`) : q6_natural ms.odin:345-351 — L 7, T 99, U 0, X 0
* `k6|tuned_v|q1` (entrée `q1_tuned_v`) : q1_tuned_v ms.odin:421-457 — L 37, T 519, U 37, X 0
* `k6|tuned|q6` (entrée `q6_tuned`) : q6_tuned ms.odin:352-366 — L 15, T 219, U 15, X 0
* `k7|natural|` (entrée `Agg`) : k7_natural ms.odin:525-528, ms.odin:541-544 — L 8, T 82, U 0, X 0
* `k7|tuned|` (entrée `Slot`) : k7_tuned ms.odin:529-532, ms.odin:550-551, ms.odin:553-568 — L 22, T 198, U 0, X 0
* `k8|natural|` (entrée `t_build`) : k8_natural ms.odin:578-590 — L 13, T 155, U 0, X 0
* `k8|tuned_it|` (entrée `ai_build`) : k8_tuned_it ms.odin:591-594, ms.odin:622-667, ms.odin:672-672 — L 51, T 334, U 41, X 0
* `k9|mt_pool|` (entrée `k9_pool_job`) : pool ms.odin:196-227 ; k9_pool ms.odin:741-747, ms.odin:766-766, ms.odin:773-774, ms.odin:790-790 ; k9_rows ms.odin:724-735 ; k9_flat ms.odin:764-765 — L 57, T 635, U 16, X 0
* `k9|natural|` (entrée `k9_natural`) : k9_natural ms.odin:721-723 ; k9_nat_alloc ms.odin:751-751 — L 4, T 117, U 0, X 0
* `k9|tuned|` (entrée `k9_rows`) : k9_rows ms.odin:724-735 ; k9_flat ms.odin:764-765 — L 14, T 283, U 12, X 0

## cpp

* `k1|natural|energy` (entrée `k1_natural`) : k1_natural ms.cpp:137-141, ms.cpp:214-214 — L 6, T 95, U 0, X 0
* `k1|soa|energy` (entrée `k1_soa`) : k1_soa ms.cpp:155-172 ; k1_soa_prep ms.cpp:190-195 — L 24, T 384, U 0, X 0
* `k3|sw_packed|` (entrée `ctr`) : k3 ms.cpp:254-254, ms.cpp:256-256, ms.cpp:260-262, ms.cpp:266-275 — L 15, T 220, U 0, X 0
* `k3|sw_padded|` (entrée `ctr`) : k3 ms.cpp:254-254, ms.cpp:256-256, ms.cpp:260-262, ms.cpp:266-275 — L 15, T 220, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4_natural`) : k4_natural ms.cpp:284-289 — L 6, T 48, U 0, X 0
* `k4|tuned|` (entrée `k4_tuned`) : k4_tuned ms.cpp:297-312 — L 16, T 156, U 0, X 6
* `k5|natural|` (entrée `k5_natural`) : k5_natural ms.cpp:354-358 — L 5, T 60, U 0, X 0
* `k5|tuned|` (entrée `k5_tuned`) : k5_tuned ms.cpp:360-370 — L 11, T 253, U 0, X 0
* `k6|mt_pool_v|q6` (entrée `q6_tuned_v`) : pool ms.cpp:72-97 ; k6_pool_run ms.cpp:494-495, ms.cpp:501-511 ; q6_tuned_v ms.cpp:440-450 ; simd_ld ms.cpp:415-418 ; q6_natural ms.cpp:396-401 — L 60, T 779, U 0, X 0
* `k6|mt_pool|q1` (entrée `q1_tuned`) : pool ms.cpp:72-97 ; k6_pool_run ms.cpp:494-495, ms.cpp:501-511 ; q1_tuned ms.cpp:453-485 ; simd_ld ms.cpp:415-418 ; q1_natural ms.cpp:402-414 — L 89, T 1135, U 0, X 0
* `k6|mt_pool|q6` (entrée `q6_tuned`) : pool ms.cpp:72-97 ; k6_pool_run ms.cpp:494-495, ms.cpp:501-511 ; q6_tuned ms.cpp:420-434 ; simd_ld ms.cpp:415-418 ; q6_natural ms.cpp:396-401 — L 64, T 816, U 0, X 0
* `k6|mt|q1` (entrée `q1_tuned`) : k6_mt_run ms.cpp:513-526 ; q1_tuned ms.cpp:453-485 ; simd_ld ms.cpp:415-418 ; q1_natural ms.cpp:402-414 — L 64, T 918, U 0, X 0
* `k6|natural|q1` (entrée `q1_natural`) : q1_natural ms.cpp:402-414 — L 13, T 156, U 0, X 0
* `k6|natural|q6` (entrée `q6_natural`) : q6_natural ms.cpp:396-401 — L 6, T 112, U 0, X 0
* `k6|tuned_v|q6` (entrée `q6_tuned_v`) : q6_tuned_v ms.cpp:440-450 ; simd_ld ms.cpp:415-418 ; q6_natural ms.cpp:396-401 — L 21, T 369, U 0, X 0
* `k6|tuned|q1` (entrée `q1_tuned`) : q1_tuned ms.cpp:453-485 ; simd_ld ms.cpp:415-418 ; q1_natural ms.cpp:402-414 — L 50, T 725, U 0, X 0
* `k6|tuned|q6` (entrée `q6_tuned`) : q6_tuned ms.cpp:420-434 ; simd_ld ms.cpp:415-418 ; q6_natural ms.cpp:396-401 — L 25, T 406, U 0, X 0
* `k7|natural|` (entrée `Agg`) : k7_natural ms.cpp:542-542, ms.cpp:551-556 — L 7, T 66, U 0, X 0
* `k7|tuned|` (entrée `Slot7`) : k7_tuned ms.cpp:543-543, ms.cpp:560-561, ms.cpp:563-577 — L 18, T 214, U 0, X 0
* `k8|natural|` (entrée `t8_build`) : k8_natural ms.cpp:587-594 — L 8, T 133, U 0, X 0
* `k8|tuned_val|` (entrée `a8v_build`) : k8_tuned_val ms.cpp:596-596, ms.cpp:614-614, ms.cpp:618-628, ms.cpp:684-684 — L 14, T 197, U 0, X 0
* `k9|mt_pool_v|` (entrée `k9_rows_v`) : pool ms.cpp:72-97 ; k9_pool_run ms.cpp:763-764, ms.cpp:790-793 ; k9_rows_v ms.cpp:739-753 ; k9_flat ms.cpp:757-757, ms.cpp:759-759 — L 49, T 623, U 0, X 0
* `k9|mt_pool|` (entrée `k9_rows`) : pool ms.cpp:72-97 ; k9_pool_run ms.cpp:763-764, ms.cpp:790-793 ; k9_rows ms.cpp:728-734 ; k9_flat ms.cpp:757-757, ms.cpp:759-759 — L 41, T 509, U 0, X 0
* `k9|mt|` (entrée `k9_rows`) : k9_mt ms.cpp:795-796 ; k9_rows ms.cpp:728-734 ; k9_flat ms.cpp:757-757, ms.cpp:759-759 — L 11, T 267, U 0, X 0
* `k9|natural|` (entrée `k9_natural`) : k9_natural ms.cpp:718-721 ; k9_nat_alloc ms.cpp:756-756, ms.cpp:758-758 — L 6, T 184, U 0, X 0
* `k9|tuned_v|` (entrée `k9_rows_v`) : k9_rows_v ms.cpp:739-753 ; k9_flat ms.cpp:757-757, ms.cpp:759-759 — L 17, T 311, U 0, X 0

## c3

* `k1|natural|energy` (entrée `k1_natural`) : k1_natural ms.c3:36-41 — L 6, T 65, U 0, X 0
* `k1|soa|energy` (entrée `k1_soa`) : k1_soa ms.c3:59-82 ; k1_soa_prep ms.c3:111-116 — L 30, T 369, U 0, X 0
* `k3|sw_packed|` (entrée `k3_worker`) : k3 ms.c3:164-178, ms.c3:181-182, ms.c3:184-185, ms.c3:188-191, ms.c3:193-193, ms.c3:195-197 — L 27, T 265, U 0, X 0
* `k3|sw_padded|` (entrée `k3_worker`) : k3 ms.c3:164-178, ms.c3:181-182, ms.c3:184-185, ms.c3:188-191, ms.c3:193-193, ms.c3:195-197 — L 27, T 265, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4_natural`) : k4_natural ms.c3:270-275 — L 6, T 35, U 0, X 0
* `k4|tuned|` (entrée `k4_tuned`) : k4_tuned ms.c3:286-306 — L 21, T 193, U 0, X 0
* `k5|natural|` (entrée `k5_natural`) : k5_natural ms.c3:364-369 — L 6, T 52, U 0, X 0
* `k5|tuned|` (entrée `k5_tuned`) : k5_tuned ms.c3:370-381 — L 12, T 294, U 0, X 0
* `k6|mt_pool_v|q1` (entrée `k6_pool_job`) : pool ms.c3:211-267 ; k6_pool ms.c3:555-571 ; k6_pool_run ms.c3:578-578, ms.c3:585-587, ms.c3:617-617 ; q1_tuned_v ms.c3:496-538 ; ld ms.c3:415-416 ; q1_natural ms.c3:433-449 — L 141, T 1466, U 0, X 0
* `k6|mt_pool|q1` (entrée `k6_pool_job`) : pool ms.c3:211-267 ; k6_pool ms.c3:555-571 ; k6_pool_run ms.c3:578-578, ms.c3:585-587, ms.c3:617-617 ; q1_tuned ms.c3:450-492 ; ld ms.c3:415-416 ; q1_natural ms.c3:433-449 — L 141, T 1474, U 0, X 0
* `k6|mt_pool|q6` (entrée `k6_pool_job`) : pool ms.c3:211-267 ; k6_pool ms.c3:555-571 ; k6_pool_run ms.c3:578-578, ms.c3:585-587, ms.c3:617-617 ; q6_tuned ms.c3:417-432 ; ld ms.c3:415-416 ; q6_natural ms.c3:406-414 — L 106, T 1053, U 0, X 0
* `k6|mt|q1` (entrée `k6_worker`) : k6_worker ms.c3:545-552 ; k6_mt_run ms.c3:597-604 ; q1_tuned ms.c3:450-492 ; ld ms.c3:415-416 ; q1_natural ms.c3:433-449 — L 78, T 1055, U 0, X 0
* `k6|natural|q1` (entrée `q1_natural`) : q1_natural ms.c3:433-449 — L 17, T 183, U 0, X 0
* `k6|natural|q6` (entrée `q6_natural`) : q6_natural ms.c3:406-414 — L 9, T 106, U 0, X 0
* `k6|tuned_v|q1` (entrée `q1_tuned_v`) : q1_tuned_v ms.c3:496-538 ; ld ms.c3:415-416 ; q1_natural ms.c3:433-449 — L 62, T 838, U 0, X 0
* `k6|tuned|q1` (entrée `q1_tuned`) : q1_tuned ms.c3:450-492 ; ld ms.c3:415-416 ; q1_natural ms.c3:433-449 — L 62, T 846, U 0, X 0
* `k6|tuned|q6` (entrée `q6_tuned`) : q6_tuned ms.c3:417-432 ; ld ms.c3:415-416 ; q6_natural ms.c3:406-414 — L 27, T 425, U 0, X 0
* `k7|natural|` (entrée `Agg`) : k7_natural ms.c3:621-621, ms.c3:634-647 — L 15, T 81, U 0, X 0
* `k7|tuned|` (entrée `Slot`) : k7_tuned ms.c3:622-622, ms.c3:655-656, ms.c3:658-678 — L 24, T 238, U 0, X 0
* `k8|natural|` (entrée `t_build`) : k8_natural ms.c3:688-697 — L 10, T 161, U 0, X 0
* `k8|tuned_it|` (entrée `ai_build`) : k8_tuned_it ms.c3:698-698, ms.c3:729-783, ms.c3:795-795 — L 57, T 351, U 0, X 0
* `k9|mt_pool|` (entrée `k9_pool_job`) : pool ms.c3:211-267 ; k9_pool ms.c3:882-887, ms.c3:912-912, ms.c3:927-928, ms.c3:947-947 ; k9_rows ms.c3:859-878 ; k9_flat ms.c3:909-910 — L 89, T 873, U 0, X 0
* `k9|natural|` (entrée `k9_natural`) : k9_natural ms.c3:850-850, ms.c3:852-858, ms.c3:893-894 — L 10, T 154, U 0, X 0
* `k9|tuned|` (entrée `k9_rows`) : k9_rows ms.c3:859-878 ; k9_flat ms.c3:909-910 — L 22, T 357, U 0, X 0

## zig

* `k1|natural|energy` (entrée `k1Natural`) : k1_natural ms.zig:54-58 — L 5, T 75, U 0, X 0
* `k1|soa|energy` (entrée `k1SoA`) : k1_soa ms.zig:73-93 ; k1_soa_prep ms.zig:120-124 — L 26, T 342, U 0, X 0
* `k3|sw_packed|` (entrée `k3Worker`) : k3 ms.zig:170-177, ms.zig:179-180, ms.zig:182-183, ms.zig:186-188, ms.zig:190-190, ms.zig:192-194 — L 19, T 300, U 0, X 0
* `k3|sw_padded|` (entrée `k3Worker`) : k3 ms.zig:170-177, ms.zig:179-180, ms.zig:182-183, ms.zig:186-188, ms.zig:190-190, ms.zig:192-194 — L 19, T 300, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4Natural`) : k4_natural ms.zig:262-268 — L 7, T 43, U 0, X 0
* `k4|tuned|` (entrée `k4Tuned`) : k4_tuned ms.zig:277-300 — L 24, T 225, U 0, X 0
* `k5|natural|` (entrée `k5Natural`) : k5_natural ms.zig:343-347 — L 5, T 48, U 0, X 0
* `k5|tuned|` (entrée `k5Tuned`) : k5_tuned ms.zig:348-360 — L 13, T 179, U 0, X 0
* `k6|mt_pool|q1` (entrée `k6PoolJob`) : pool ms.zig:208-259 ; k6_pool ms.zig:476-480 ; k6_pool_run ms.zig:485-485, ms.zig:491-493, ms.zig:516-516 ; k6_worker ms.zig:467-473 ; q1_tuned ms.zig:419-459 — L 110, T 1341, U 1, X 0
* `k6|mt_pool|q6` (entrée `k6PoolJob`) : pool ms.zig:208-259 ; k6_pool ms.zig:476-480 ; k6_pool_run ms.zig:485-485, ms.zig:491-493, ms.zig:516-516 ; k6_worker ms.zig:467-473 ; q6_tuned ms.zig:390-403 — L 83, T 930, U 1, X 0
* `k6|mt|q1` (entrée `k6Worker`) : k6_worker ms.zig:467-473 ; k6_mt_run ms.zig:495-499 ; q1_tuned ms.zig:419-459 — L 53, T 903, U 0, X 0
* `k6|natural|q1` (entrée `q1Natural`) : q1_natural ms.zig:404-417 — L 14, T 175, U 0, X 0
* `k6|natural|q6` (entrée `q6Natural`) : q6_natural ms.zig:382-388 — L 7, T 111, U 0, X 0
* `k6|tuned|q1` (entrée `q1Tuned`) : q1_tuned ms.zig:419-459 — L 41, T 711, U 0, X 0
* `k6|tuned|q6` (entrée `q6Tuned`) : q6_tuned ms.zig:390-403 — L 14, T 300, U 0, X 0
* `k7|natural|` (entrée `Agg`) : k7_natural ms.zig:520-520, ms.zig:532-538 — L 8, T 96, U 0, X 0
* `k7|tuned|` (entrée `Slot`) : k7_tuned ms.zig:521-521, ms.zig:545-546, ms.zig:548-565 — L 21, T 266, U 0, X 0
* `k8|natural|` (entrée `tBuild`) : k8_natural ms.zig:578-596 — L 19, T 202, U 0, X 0
* `k8|tuned_it|` (entrée `aiBuild`) : k8_tuned_it ms.zig:597-597, ms.zig:637-690, ms.zig:697-697 — L 56, T 454, U 0, X 0
* `k9|mt_pool|` (entrée `k9PoolJob`) : pool ms.zig:208-259 ; k9_pool ms.zig:773-777, ms.zig:808-808, ms.zig:819-820, ms.zig:832-832 ; k9_rows ms.zig:753-771 ; k9_flat ms.zig:805-806 — L 82, T 850, U 1, X 0
* `k9|natural|` (entrée `k9Natural`) : k9_natural ms.zig:748-752, ms.zig:781-782 — L 7, T 150, U 0, X 0
* `k9|tuned|` (entrée `k9Rows`) : k9_rows ms.zig:753-771 ; k9_flat ms.zig:805-806 — L 21, T 321, U 0, X 0

## rust

* `k1|natural|energy` (entrée `k1_natural`) : k1_natural ms.rs:142-145 — L 4, T 72, U 0, X 0
* `k1|soa|energy` (entrée `k1_soa`) : k1_soa ms.rs:159-177 ; k1_soa_prep ms.rs:208-208, ms.rs:211-211 ; abuf ms.rs:27-47 — L 42, T 641, U 22, X 12
* `k3|sw_packed|` (entrée `Padded`) : k3 ms.rs:241-242, ms.rs:244-245, ms.rs:247-249, ms.rs:254-268 — L 22, T 227, U 0, X 0
* `k3|sw_padded|` (entrée `Padded`) : k3 ms.rs:241-242, ms.rs:244-245, ms.rs:247-249, ms.rs:254-268 — L 22, T 227, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4_natural`) : k4_natural ms.rs:274-277 — L 4, T 50, U 0, X 0
* `k4|tuned|` (entrée `k4_tuned_avx512`) : k4_tuned ms.rs:284-309 — L 26, T 190, U 22, X 7
* `k5|natural|` (entrée `k5_natural`) : k5_natural ms.rs:352-355 — L 4, T 56, U 0, X 0
* `k5|tuned|` (entrée `k5_tuned`) : k5_tuned ms.rs:359-372 — L 14, T 246, U 13, X 7
* `k6|mt_pool_v|q6` (entrée `K6Job`) : pool ms.rs:53-106 ; k6_job ms.rs:504-519 ; k6_pool_run ms.rs:529-530, ms.rs:532-534 ; q6_tuned_v ms.rs:418-439 ; q6_natural ms.rs:392-401 — L 106, T 1239, U 30, X 13
* `k6|mt_pool|q1` (entrée `K6Job`) : pool ms.rs:53-106 ; k6_job ms.rs:504-519 ; k6_pool_run ms.rs:529-530, ms.rs:532-534 ; q1_tuned ms.rs:456-501 ; q1_natural ms.rs:440-454 — L 135, T 1601, U 54, X 24
* `k6|natural|q1` (entrée `q1_natural`) : q1_natural ms.rs:440-454 — L 15, T 173, U 0, X 0
* `k6|natural|q6` (entrée `q6_natural`) : q6_natural ms.rs:392-401 — L 10, T 109, U 0, X 0
* `k6|tuned_v|q6` (entrée `q6_tuned_v`) : q6_tuned_v ms.rs:418-439 ; q6_natural ms.rs:392-401 — L 32, T 470, U 21, X 13
* `k6|tuned|q1` (entrée `q1_tuned`) : q1_tuned ms.rs:456-501 ; q1_natural ms.rs:440-454 — L 61, T 832, U 45, X 24
* `k7|natural|` (entrée `HashMap`) : k7_natural ms.rs:587-592 — L 6, T 76, U 0, X 0
* `k7|tuned|` (entrée `Slot7`) : k7_tuned ms.rs:577-579, ms.rs:597-598, ms.rs:600-619 — L 24, T 264, U 1, X 1
* `k8|natural|` (entrée `t_build`) : k8_natural ms.rs:631-640 — L 10, T 177, U 0, X 0
* `k8|tuned_it|` (entrée `ai_build`) : k8_tuned_it ms.rs:641-642, ms.rs:710-760, ms.rs:769-769 — L 54, T 408, U 8, X 0
* `k9|mt_pool_v|` (entrée `K9Job`) : pool ms.rs:53-106 ; k9_job ms.rs:873-883 ; k9_flat ms.rs:931-931, ms.rs:936-936 ; k9_pool_call ms.rs:940-940, ms.rs:956-956 ; k9_rows_v ms.rs:847-870 ; abuf ms.rs:27-47 — L 113, T 1352, U 39, X 6
* `k9|mt_pool|` (entrée `K9Job`) : pool ms.rs:53-106 ; k9_job ms.rs:873-883 ; k9_flat ms.rs:931-931, ms.rs:936-936 ; k9_pool_call ms.rs:940-940, ms.rs:956-956 ; k9_rows ms.rs:829-841 ; abuf ms.rs:27-47 — L 101, T 1221, U 16, X 0
* `k9|natural|` (entrée `k9_natural`) : k9_natural ms.rs:812-819 ; k9_nat_alloc ms.rs:888-889 — L 10, T 124, U 0, X 0
* `k9|tuned_v|` (entrée `k9_rows_v`) : k9_rows_v ms.rs:847-870 ; k9_flat ms.rs:931-931, ms.rs:936-936 ; k9_v_call ms.rs:941-945 ; abuf ms.rs:27-47 — L 52, T 726, U 32, X 6

## nim

* `k1|natural|energy` (entrée `k1Natural`) : k1_natural ms.nim:52-53 — L 2, T 56, U 0, X 0
* `k1|soa|energy` (entrée `k1SoA`) : k1_soa ms.nim:28-30, ms.nim:32-35, ms.nim:37-37, ms.nim:39-43, ms.nim:66-80, ms.nim:109-112 ; k1_push ms.nim:55-55, ms.nim:81-81 ; aa_decl ms.nim:8-8 — L 35, T 541, U 19, X 13
* `k3|sw_packed|` (entrée `k3Worker`) : k3 ms.nim:148-156, ms.nim:158-159, ms.nim:161-162, ms.nim:164-166, ms.nim:169-171 — L 19, T 236, U 1, X 0
* `k3|sw_padded|` (entrée `k3Worker`) : k3 ms.nim:148-156, ms.nim:158-159, ms.nim:161-162, ms.nim:164-166, ms.nim:169-171 — L 19, T 236, U 1, X 0
* `k4|natural_unsorted|` (entrée `k4Natural`) : k4_natural ms.nim:230-232 — L 3, T 31, U 0, X 0
* `k4|tuned|` (entrée `k4Tuned`) : k4_tuned ms.nim:237-257 — L 21, T 273, U 1, X 8
* `k5|natural|` (entrée `k5Natural`) : k5_natural ms.nim:300-301 — L 2, T 43, U 1, X 0
* `k5|tuned|` (entrée `k5Tuned`) : k5_tuned ms.nim:28-28, ms.nim:31-31, ms.nim:34-34, ms.nim:36-38, ms.nim:302-314 — L 19, T 307, U 5, X 6
* `k6|mt_pool_v|q1` (entrée `k6PoolJob`) : pool ms.nim:184-228 ; k6_pool ms.nim:488-501, ms.nim:508-508, ms.nim:513-515, ms.nim:539-539 ; q1_tuned_v ms.nim:237-239, ms.nim:243-244, ms.nim:381-387, ms.nim:390-405, ms.nim:437-474 ; k6v_push ms.nim:406-406, ms.nim:475-475 ; q1_natural ms.nim:347-357 — L 143, T 1869, U 42, X 26
* `k6|mt_pool_v|q6` (entrée `k6PoolJob`) : pool ms.nim:184-228 ; k6_pool ms.nim:488-501, ms.nim:508-508, ms.nim:513-515, ms.nim:539-539 ; q6_tuned_v ms.nim:237-239, ms.nim:243-244, ms.nim:381-389, ms.nim:395-395, ms.nim:397-397, ms.nim:401-403, ms.nim:412-432 ; k6v_push ms.nim:406-406, ms.nim:475-475 ; q6_natural ms.nim:337-340 — L 110, T 1196, U 25, X 18
* `k6|natural|q1` (entrée `q1Natural`) : q1_natural ms.nim:347-357 — L 11, T 162, U 0, X 0
* `k6|natural|q6` (entrée `q6Natural`) : q6_natural ms.nim:337-340 — L 4, T 95, U 0, X 0
* `k6|tuned_v|q1` (entrée `q1TunedV`) : q1_tuned_v ms.nim:237-239, ms.nim:243-244, ms.nim:381-387, ms.nim:390-405, ms.nim:437-474 ; k6v_push ms.nim:406-406, ms.nim:475-475 ; q1_natural ms.nim:347-357 — L 79, T 1389, U 40, X 26
* `k6|tuned_v|q6` (entrée `q6TunedV`) : q6_tuned_v ms.nim:237-239, ms.nim:243-244, ms.nim:381-389, ms.nim:395-395, ms.nim:397-397, ms.nim:401-403, ms.nim:412-432 ; k6v_push ms.nim:406-406, ms.nim:475-475 ; q6_natural ms.nim:337-340 — L 46, T 716, U 23, X 18
* `k7|natural|` (entrée `Agg`) : k7_natural ms.nim:542-545, ms.nim:557-561 — L 9, T 65, U 1, X 0
* `k7|tuned|` (entrée `Slot`) : k7_tuned ms.nim:44-44, ms.nim:546-548, ms.nim:566-567, ms.nim:569-586 ; aa_decl ms.nim:8-8 — L 25, T 289, U 17, X 0
* `k8|natural|` (entrée `tBuild`) : k8_natural ms.nim:595-598, ms.nim:602-608 — L 11, T 104, U 0, X 0
* `k8|tuned_it|` (entrée `aiBuild`) : k8_tuned_it ms.nim:599-601, ms.nim:621-621, ms.nim:654-694, ms.nim:702-702 — L 46, T 330, U 42, X 0
* `k9|mt_pool_v|` (entrée `k9PoolJob`) : pool ms.nim:184-228 ; k9_pool ms.nim:782-789, ms.nim:832-832, ms.nim:842-843, ms.nim:852-852 ; k9_rows_v ms.nim:29-29, ms.nim:39-39, ms.nim:753-779 ; k9_flat ms.nim:829-830 ; aa_decl ms.nim:8-8 — L 84, T 896, U 23, X 6
* `k9|mt_pool|` (entrée `k9PoolJob`) : pool ms.nim:184-228 ; k9_pool ms.nim:782-789, ms.nim:832-832, ms.nim:842-843, ms.nim:852-852 ; k9_rows ms.nim:744-752 ; k9_flat ms.nim:829-830 ; aa_decl ms.nim:8-8 — L 69, T 682, U 14, X 0
* `k9|mt|` (entrée `k9Worker`) : k9_mt ms.nim:790-791, ms.nim:845-847 ; k9_rows ms.nim:744-752 ; k9_flat ms.nim:829-830 ; aa_decl ms.nim:8-8 — L 17, T 376, U 12, X 0
* `k9|natural|` (entrée `k9Natural`) : k9_natural ms.nim:735-738, ms.nim:795-799 — L 9, T 160, U 0, X 0
* `k9|tuned_v|` (entrée `k9RowsV`) : k9_rows_v ms.nim:29-29, ms.nim:39-39, ms.nim:753-779 ; k9_flat ms.nim:829-830 ; aa_decl ms.nim:8-8 — L 27, T 472, U 20, X 6

## d

* `k1|natural|energy` (entrée `k1Natural`) : k1_natural ms.d:52-56 — L 5, T 66, U 0, X 0
* `k1|soa|energy` (entrée `k1SoA`) : k1_soa ms.d:26-27, ms.d:69-86, ms.d:112-116 — L 25, T 328, U 2, X 0
* `k3|sw_packed|` (entrée `Padded`) : k3 ms.d:158-159, ms.d:161-161, ms.d:163-164, ms.d:166-167, ms.d:171-179 — L 16, T 248, U 0, X 0
* `k3|sw_padded|` (entrée `Padded`) : k3 ms.d:158-159, ms.d:161-161, ms.d:163-164, ms.d:166-167, ms.d:171-179 — L 16, T 248, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4Natural`) : k4_natural ms.d:226-226 — L 1, T 41, U 0, X 0
* `k4|tuned|` (entrée `k4Tuned`) : k4_tuned ms.d:29-29, ms.d:231-248 — L 19, T 184, U 1, X 1
* `k5|natural|` (entrée `k5Natural`) : k5_natural ms.d:289-293 — L 5, T 53, U 0, X 0
* `k5|tuned|` (entrée `k5Tuned`) : k5_tuned ms.d:26-26, ms.d:294-307 — L 15, T 229, U 4, X 0
* `k6|mt_pool_v|q6` (entrée `k6PoolJob`) : pool ms.d:193-223 ; k6_pool ms.d:425-431, ms.d:437-437, ms.d:442-444, ms.d:466-466 ; q6_tuned_v ms.d:407-422 ; k6_simd_v ms.d:28-29, ms.d:358-364, ms.d:366-366 ; q6_natural ms.d:329-334 — L 75, T 896, U 4, X 0
* `k6|mt_pool|q1` (entrée `k6PoolJob`) : pool ms.d:193-223 ; k6_pool ms.d:425-431, ms.d:437-437, ms.d:442-444, ms.d:466-466 ; q1_tuned ms.d:367-400 ; k6_simd ms.d:28-29, ms.d:358-366 ; q1_natural ms.d:346-354 — L 97, T 1287, U 4, X 0
* `k6|natural|q1` (entrée `q1Natural`) : q1_natural ms.d:346-354 — L 9, T 159, U 0, X 0
* `k6|natural|q6` (entrée `q6Natural`) : q6_natural ms.d:329-334 — L 6, T 105, U 0, X 0
* `k6|tuned_v|q6` (entrée `q6TunedV`) : q6_tuned_v ms.d:407-422 ; k6_simd_v ms.d:28-29, ms.d:358-364, ms.d:366-366 ; q6_natural ms.d:329-334 — L 32, T 493, U 3, X 0
* `k6|tuned|q1` (entrée `q1Tuned`) : q1_tuned ms.d:367-400 ; k6_simd ms.d:28-29, ms.d:358-366 ; q1_natural ms.d:346-354 — L 54, T 884, U 3, X 0
* `k7|natural|` (entrée `Agg`) : k7_natural ms.d:470-470, ms.d:479-482 — L 5, T 66, U 0, X 0
* `k7|tuned|` (entrée `Slot`) : k7_tuned ms.d:471-471, ms.d:487-487, ms.d:489-502 — L 16, T 225, U 1, X 0
* `k8|natural|` (entrée `tBuild`) : k8_natural ms.d:512-519 — L 8, T 106, U 0, X 0
* `k8|tuned_it|` (entrée `aiBuild`) : k8_tuned_it ms.d:520-520, ms.d:546-578, ms.d:587-587 — L 35, T 354, U 1, X 0
* `k9|mt_pool|` (entrée `k9PoolJob`) : pool ms.d:193-223 ; k9_pool ms.d:634-638, ms.d:646-646, ms.d:669-669, ms.d:685-685 ; k9_rows ms.d:27-27, ms.d:620-632 ; k9_flat ms.d:642-642, ms.d:644-644 — L 55, T 604, U 2, X 0
* `k9|natural|` (entrée `k9Natural`) : k9_natural ms.d:613-615, ms.d:641-641, ms.d:643-643 — L 5, T 146, U 0, X 0
* `k9|tuned|` (entrée `k9Rows`) : k9_rows ms.d:27-27, ms.d:620-632 ; k9_flat ms.d:642-642, ms.d:644-644 — L 16, T 274, U 1, X 0

## ada

* `k1|natural|energy` (entrée `K1_Natural`) : k1_natural ms.adb:123-130 — L 8, T 71, U 0, X 0
* `k1|soa|energy` (entrée `K1_Soa`) : k1_soa ms.adb:150-168, ms.adb:203-219 — L 36, T 420, U 19, X 0
* `k3|sw_packed|` (entrée `Worker`) : k3 ms.adb:289-340, ms.adb:350-356 — L 57, T 397, U 57, X 0
* `k3|sw_padded|` (entrée `Worker`) : k3 ms.adb:289-340, ms.adb:350-356 — L 57, T 397, U 57, X 0
* `k4|natural_unsorted|` (entrée `K4_Natural`) : k4_natural ms.adb:370-379 — L 10, T 48, U 0, X 0
* `k4|swar|` (entrée `K4_Swar`) : k4_swar ms.adb:437-467 — L 31, T 280, U 31, X 0
* `k4|tuned|` (entrée `K4_Tuned`) : k4_tuned ms.adb:391-391, ms.adb:393-393, ms.adb:395-402, ms.adb:403-429 — L 35, T 306, U 1, X 4
* `k5|natural|` (entrée `K5_Natural`) : k5_natural ms.adb:499-506 — L 8, T 48, U 0, X 0
* `k5|tuned|` (entrée `K5_Tuned`) : k5_tuned ms.adb:104-104, ms.adb:106-109, ms.adb:508-534 — L 32, T 464, U 27, X 2
* `k6|mt_pool_v|q1` (entrée `Pool_Worker`) : k6_pool ms.adb:803-805, ms.adb:832-878, ms.adb:894-899, ms.adb:904-911, ms.adb:915-915 ; q1_tuned_v ms.adb:393-393, ms.adb:401-402, ms.adb:649-649, ms.adb:651-651, ms.adb:653-664, ms.adb:667-668, ms.adb:671-681, ms.adb:728-794 ; q1_natural ms.adb:584-600 — L 179, T 1985, U 69, X 10
* `k6|mt_pool_v|q6` (entrée `Pool_Worker`) : k6_pool ms.adb:803-805, ms.adb:832-878, ms.adb:894-899, ms.adb:904-911, ms.adb:915-915 ; q6_tuned_v ms.adb:393-393, ms.adb:401-402, ms.adb:649-649, ms.adb:651-651, ms.adb:653-658, ms.adb:665-666, ms.adb:669-670, ms.adb:677-677, ms.adb:679-681, ms.adb:688-721 ; q6_natural ms.adb:563-572 — L 128, T 1216, U 35, X 6
* `k6|natural|q1` (entrée `Q1_Natural`) : q1_natural ms.adb:584-600 — L 17, T 213, U 0, X 0
* `k6|natural|q6` (entrée `Q6_Natural`) : q6_natural ms.adb:563-572 — L 10, T 116, U 0, X 0
* `k6|tuned_v|q1` (entrée `Q1_Tuned_V`) : q1_tuned_v ms.adb:393-393, ms.adb:401-402, ms.adb:649-649, ms.adb:651-651, ms.adb:653-664, ms.adb:667-668, ms.adb:671-681, ms.adb:728-794 ; q1_natural ms.adb:584-600 — L 114, T 1582, U 69, X 10
* `k6|tuned_v|q6` (entrée `Q6_Tuned_V`) : q6_tuned_v ms.adb:393-393, ms.adb:401-402, ms.adb:649-649, ms.adb:651-651, ms.adb:653-658, ms.adb:665-666, ms.adb:669-670, ms.adb:677-677, ms.adb:679-681, ms.adb:688-721 ; q6_natural ms.adb:563-572 — L 63, T 813, U 35, X 6
* `k7|natural|` (entrée `U32_Maps`) : k7_natural ms.adb:976-982, ms.adb:1001-1005, ms.adb:1007-1015 — L 21, T 162, U 0, X 0
* `k7|tuned|` (entrée `Slot_Arr`) : k7_tuned ms.adb:100-101, ms.adb:983-988, ms.adb:1023-1032, ms.adb:1034-1050 — L 35, T 330, U 27, X 0
* `k8|natural|` (entrée `T_Build`) : k8_natural ms.adb:1068-1094 — L 27, T 195, U 0, X 0
* `k8|tuned|` (entrée `A_Build`) : k8_tuned ms.adb:1097-1124 — L 28, T 252, U 23, X 0
* `k9|mt_pool|` (entrée `Pool_Worker`) : k9_pool ms.adb:1399-1426, ms.adb:1429-1434, ms.adb:1440-1446, ms.adb:1458-1458 ; k9_rows ms.adb:1331-1340 — L 52, T 346, U 10, X 0
* `k9|natural|` (entrée `K9_Natural`) : k9_natural ms.adb:1323-1330 — L 8, T 93, U 0, X 0
* `k9|tuned|` (entrée `K9_Rows`) : k9_rows ms.adb:1331-1340 — L 10, T 111, U 10, X 0

## chapel

* `k1|natural|energy` (entrée `k1Natural`) : k1_natural ms.chpl:33-37 — L 5, T 62, U 0, X 0
* `k1|soa|energy` (entrée `k1Soa`) : k1_soa ms.chpl:45-49, ms.chpl:67-68 — L 7, T 165, U 0, X 0
* `k3|sw_packed|` (entrée `stride`) : k3 ms.chpl:122-122, ms.chpl:125-125, ms.chpl:130-136 — L 9, T 115, U 0, X 0
* `k3|sw_padded|` (entrée `stride`) : k3 ms.chpl:122-122, ms.chpl:125-125, ms.chpl:130-136 — L 9, T 115, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4Natural`) : k4_natural ms.chpl:145-149 — L 5, T 42, U 0, X 0
* `k4|tuned|` (entrée `k4Tuned`) : k4_tuned ms.chpl:159-184 — L 26, T 246, U 3, X 13
* `k5|natural|` (entrée `k5Natural`) : k5_natural ms.chpl:225-229 — L 5, T 64, U 0, X 0
* `k5|tuned_v|` (entrée `k5TunedV`) : k5_tuned_v ms.chpl:241-258 — L 18, T 315, U 6, X 12
* `k5|tuned|` (entrée `k5Tuned`) : k5_tuned ms.chpl:232-236 — L 5, T 64, U 0, X 0
* `k6|mt_pool_v|q1` (entrée `coforall`) : k6_pool_v ms.chpl:483-490 ; q1_tuned_v ms.chpl:159-161, ms.chpl:166-166, ms.chpl:349-357, ms.chpl:359-360, ms.chpl:363-371, ms.chpl:404-458 ; ptrs ms.chpl:464-465 — L 87, T 1419, U 13, X 49
* `k6|mt_pool_v|q6` (entrée `coforall`) : k6_pool_v ms.chpl:483-490 ; q6_tuned_v ms.chpl:159-161, ms.chpl:165-166, ms.chpl:350-353, ms.chpl:355-355, ms.chpl:358-358, ms.chpl:361-363, ms.chpl:377-400 ; ptrs ms.chpl:464-465 — L 48, T 770, U 8, X 27
* `k6|mt|q6` (entrée `coforall`) : k6_mt ms.chpl:472-479 ; q6_tuned ms.chpl:288-296 — L 17, T 293, U 0, X 0
* `k6|natural|q1` (entrée `q1Natural`) : q1_natural ms.chpl:297-310 — L 14, T 172, U 0, X 0
* `k6|natural|q6` (entrée `q6Natural`) : q6_natural ms.chpl:281-287 — L 7, T 124, U 0, X 0
* `k6|tuned_v|q1` (entrée `q1TunedV`) : q1_tuned_v ms.chpl:159-161, ms.chpl:166-166, ms.chpl:349-357, ms.chpl:359-360, ms.chpl:363-371, ms.chpl:404-458 ; ptrs ms.chpl:464-465 — L 79, T 1283, U 13, X 49
* `k6|tuned_v|q6` (entrée `q6TunedV`) : q6_tuned_v ms.chpl:159-161, ms.chpl:165-166, ms.chpl:350-353, ms.chpl:355-355, ms.chpl:358-358, ms.chpl:361-363, ms.chpl:377-400 ; ptrs ms.chpl:464-465 — L 40, T 634, U 8, X 27
* `k6|tuned|q6` (entrée `q6Tuned`) : q6_tuned ms.chpl:288-296 — L 9, T 157, U 0, X 0
* `k7|natural|` (entrée `Agg`) : k7_natural ms.chpl:506-506, ms.chpl:515-523 — L 10, T 91, U 0, X 0
* `k7|tuned|` (entrée `Slot`) : k7_tuned ms.chpl:507-507, ms.chpl:527-527, ms.chpl:529-544 — L 18, T 209, U 1, X 0
* `k8|natural|` (entrée `tBuild`) : k8_natural ms.chpl:553-564 — L 12, T 134, U 0, X 0
* `k8|tuned_it|` (entrée `aiBuild`) : k8_tuned_it ms.chpl:565-565, ms.chpl:598-633, ms.chpl:640-640 — L 38, T 375, U 0, X 0
* `k9|mt_pool_v|` (entrée `k9ParV`) : k9_par_v ms.chpl:727-729 ; k9_rows_v ms.chpl:699-724 — L 29, T 380, U 9, X 12
* `k9|mt|` (entrée `k9Par`) : k9_par ms.chpl:689-693 — L 5, T 90, U 0, X 0
* `k9|natural|` (entrée `k9Natural`) : k9_natural ms.chpl:680-683 — L 4, T 88, U 0, X 0
* `k9|tuned_v|` (entrée `k9RowsV`) : k9_rows_v ms.chpl:699-724 — L 26, T 321, U 8, X 12
* `k9|tuned|` (entrée `k9Rows`) : k9_rows ms.chpl:684-688 — L 5, T 93, U 0, X 0

## fortran

* `k1|natural|energy` (entrée `k1_natural`) : k1_natural ms.f90:124-132 — L 8, T 87, U 0, X 0
* `k1|soa|energy` (entrée `k1_soa`) : k1_soa tuned.f90:20-28, ms.f90:138-139, ms.f90:151-155 ; align32 ms.f90:97-105 — L 25, T 308, U 0, X 0
* `k3|sw_packed|` (entrée `stride`) : k3 ms.f90:239-240, ms.f90:246-246, ms.f90:250-266 — L 20, T 132, U 0, X 0
* `k3|sw_padded|` (entrée `stride`) : k3 ms.f90:239-240, ms.f90:246-246, ms.f90:250-266 — L 20, T 132, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4_natural`) : k4_natural ms.f90:272-281 — L 9, T 73, U 0, X 0
* `k4|swar|` (entrée `k4_swar`) : k4_swar tuned.f90:133-157 — L 25, T 300, U 0, X 0
* `k5|natural|` (entrée `k5_natural`) : k5_natural ms.f90:328-332 — L 4, T 46, U 0, X 0
* `k5|rq_acc16|` (entrée `k5_acc16`) : k5_acc16 tuned.f90:162-174 — L 13, T 207, U 0, X 0
* `k5|tuned|` (entrée `k5_tuned`) : k5_tuned tuned.f90:31-45 — L 15, T 189, U 0, X 0
* `k6|mt|q1` (entrée `q1_tuned`) : k6_mt ms.f90:428-438 ; q1_tuned tuned.f90:61-94 — L 45, T 557, U 0, X 0
* `k6|mt|q6` (entrée `q6_tuned`) : k6_mt ms.f90:428-438 ; q6_tuned tuned.f90:46-57 — L 23, T 276, U 0, X 0
* `k6|natural|q1` (entrée `q1_natural`) : q1_natural ms.f90:389-407 — L 18, T 190, U 0, X 0
* `k6|natural|q6` (entrée `q6_natural`) : q6_natural ms.f90:380-388 — L 8, T 99, U 0, X 0
* `k6|tuned|q1` (entrée `q1_tuned`) : q1_tuned tuned.f90:61-94 — L 34, T 448, U 0, X 0
* `k6|tuned|q6` (entrée `q6_tuned`) : q6_tuned tuned.f90:46-57 — L 12, T 167, U 0, X 0
* `k7|natural|` (entrée `hnode`) : k7_natural ms.f90:476-482, ms.f90:494-494, ms.f90:507-525 ; k7_params ms.f90:495-495 — L 28, T 245, U 0, X 0
* `k7|tuned_oa|` (entrée `slot`) : k7_tuned_oa ms.f90:545-557 ; k7_slot ms.f90:483-486, ms.f90:493-493 ; k7_params ms.f90:495-495 — L 19, T 227, U 0, X 0
* `k7|tuned|` (entrée `touch`) : k7_tuned ms.f90:497-498, ms.f90:568-587 ; k7_slot ms.f90:483-486, ms.f90:493-493 ; k7_params ms.f90:495-495 — L 28, T 309, U 0, X 0
* `k8|natural|` (entrée `t_build`) : k8_natural ms.f90:607-610, ms.f90:725-751 — L 31, T 227, U 0, X 0
* `k8|tuned_val|` (entrée `val_build`) : k8_tuned_val ms.f90:615-619, ms.f90:641-648, ms.f90:652-669, ms.f90:817-817 — L 32, T 250, U 0, X 0
* `k9|mt|` (entrée `k9_cols`) : k9_mt ms.f90:921-925 ; k9_cols tuned.f90:96-107 ; k9_flat ms.f90:888-889, ms.f90:896-898 ; align64 ms.f90:106-114 — L 31, T 390, U 0, X 0
* `k9|natural|` (entrée `k9_natural`) : k9_natural ms.f90:878-883, ms.f90:887-887, ms.f90:900-900 — L 7, T 189, U 0, X 0

## swift

* `k1|natural|energy` (entrée `k1Natural`) : k1_natural ms.swift:126-132 — L 7, T 68, U 0, X 0
* `k1|soa|energy` (entrée `k1SoA`) : k1_soa ms.swift:149-177, ms.swift:200-207 ; simd_f ms.swift:90-90, ms.swift:106-109 ; aligned ms.swift:47-49 — L 45, T 633, U 14, X 0
* `k3|sw_packed|` (entrée `runThreads`) : k3 ms.swift:260-260, ms.swift:263-266, ms.swift:270-277 ; threads ms.swift:51-57 — L 20, T 241, U 2, X 0
* `k3|sw_padded|` (entrée `runThreads`) : k3 ms.swift:260-260, ms.swift:263-266, ms.swift:270-277 ; threads ms.swift:51-57 — L 20, T 241, U 2, X 0
* `k4|natural_unsorted|` (entrée `k4Natural`) : k4_natural ms.swift:286-292 — L 7, T 45, U 0, X 0
* `k4|tuned|` (entrée `k4Tuned`) : k4_tuned ms.swift:303-324 — L 22, T 199, U 9, X 0
* `k5|natural|` (entrée `k5Natural`) : k5_natural ms.swift:379-383 — L 5, T 55, U 0, X 0
* `k5|tuned|` (entrée `k5Tuned`) : k5_tuned ms.swift:384-395 ; simd_f ms.swift:90-90, ms.swift:106-109 — L 17, T 289, U 6, X 0
* `k6|mt_pool|q1` (entrée `Pool`) : k6_pool ms.swift:569-569, ms.swift:581-585, ms.swift:593-593 ; pool ms.swift:62-89 ; q1_tuned ms.swift:459-469, ms.swift:488-540 ; colsp ms.swift:421-424, ms.swift:559-565 ; part ms.swift:566-566 ; simd_i ms.swift:91-91, ms.swift:94-103 — L 120, T 1586, U 40, X 0
* `k6|mt_pool|q6` (entrée `Pool`) : k6_pool ms.swift:569-569, ms.swift:581-585, ms.swift:593-593 ; pool ms.swift:62-89 ; q6_tuned ms.swift:452-458, ms.swift:471-484 ; colsp ms.swift:421-424, ms.swift:559-565 ; part ms.swift:566-566 ; simd_i ms.swift:91-91, ms.swift:94-103 — L 79, T 924, U 18, X 0
* `k6|mt|q1` (entrée `runThreads`) : k6_mt ms.swift:575-579 ; threads ms.swift:51-57 ; q1_tuned ms.swift:459-469, ms.swift:488-540 ; colsp ms.swift:421-424, ms.swift:559-565 ; part ms.swift:566-566 ; simd_i ms.swift:91-91, ms.swift:94-103 — L 97, T 1462, U 40, X 0
* `k6|natural|q1` (entrée `q1Natural`) : q1_natural ms.swift:437-450 ; cols ms.swift:416-419, ms.swift:544-547 ; q1agg ms.swift:425-427 — L 25, T 304, U 0, X 0
* `k6|natural|q6` (entrée `q6Natural`) : q6_natural ms.swift:428-436 ; cols ms.swift:416-419, ms.swift:544-547 — L 17, T 213, U 0, X 0
* `k6|tuned|q1` (entrée `q1Tuned`) : q1_tuned ms.swift:459-469, ms.swift:488-540 ; colsp ms.swift:421-424, ms.swift:559-565 ; part ms.swift:566-566 ; simd_i ms.swift:91-91, ms.swift:94-103 — L 85, T 1310, U 39, X 0
* `k6|tuned|q6` (entrée `q6Tuned`) : q6_tuned ms.swift:452-458, ms.swift:471-484 ; colsp ms.swift:421-424, ms.swift:559-565 ; simd_i ms.swift:91-91, ms.swift:94-103 — L 43, T 629, U 16, X 0
* `k7|natural|` (entrée `Agg`) : k7_natural ms.swift:598-605, ms.swift:623-624 — L 10, T 78, U 0, X 0
* `k7|tuned|` (entrée `Slot`) : k7_tuned ms.swift:607-611, ms.swift:676-676, ms.swift:678-691 ; aligned ms.swift:47-49 — L 23, T 243, U 14, X 0
* `k8|natural|` (entrée `tBuild`) : k8_natural ms.swift:705-723 — L 19, T 130, U 0, X 0
* `k8|tuned_it|` (entrée `aiBuild`) : k8_tuned_it ms.swift:725-729, ms.swift:769-814, ms.swift:818-818, ms.swift:823-823 — L 53, T 374, U 13, X 0
* `k9|mt_pool|` (entrée `Pool`) : k9_pool ms.swift:941-941, ms.swift:952-953, ms.swift:965-965 ; pool ms.swift:62-89 ; k9_rows ms.swift:104-104, ms.swift:878-893 ; k9_flat ms.swift:939-939 ; aligned ms.swift:47-49 — L 53, T 610, U 10, X 0
* `k9|natural|` (entrée `k9Natural`) : k9_natural ms.swift:862-868, ms.swift:897-898 — L 9, T 160, U 0, X 0
* `k9|tuned|` (entrée `k9Rows`) : k9_rows ms.swift:104-104, ms.swift:878-893 ; k9_flat ms.swift:939-939 ; aligned ms.swift:47-49 — L 21, T 358, U 10, X 0

## julia

* `k1|natural|energy` (entrée `k1_natural`) : k1_natural ms.jl:19-25 — L 7, T 55, U 0, X 0
* `k1|soa|energy` (entrée `k1_soa`) : k1_soa ms.jl:34-40, ms.jl:56-56 — L 8, T 115, U 3, X 0
* `k3|sw_packed|` (entrée `k3_worker`) : k3 ms.jl:92-103, ms.jl:105-106, ms.jl:108-108, ms.jl:114-115 — L 17, T 131, U 0, X 0
* `k3|sw_padded|` (entrée `k3_worker`) : k3 ms.jl:92-103, ms.jl:105-106, ms.jl:108-108, ms.jl:114-115 — L 17, T 131, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4_natural`) : k4_natural ms.jl:123-131 — L 9, T 33, U 0, X 0
* `k4|tuned|` (entrée `k4_tuned`) : k4_tuned ms.jl:143-174 — L 32, T 279, U 16, X 0
* `k5|natural|` (entrée `k5_natural`) : k5_natural ms.jl:219-225 — L 7, T 43, U 0, X 0
* `k5|tuned_v|` (entrée `k5_tuned_v`) : k5_tuned_v ms.jl:236-286 — L 51, T 803, U 49, X 0
* `k6|mt_pool_v|q1` (entrée `q1_tuned_v`) : k6_mt_pool_v ms.jl:796-800 ; q1_tuned_v ms.jl:445-779 ; q1_natural ms.jl:326-334 — L 349, T 5857, U 324, X 0
* `k6|mt_pool_v|q6` (entrée `q6_tuned_v`) : k6_mt_pool_v ms.jl:796-800 ; q6_tuned_v ms.jl:388-440 ; q6_natural ms.jl:308-316 — L 67, T 1113, U 46, X 0
* `k6|mt|q6` (entrée `q6_tuned`) : k6_mt ms.jl:788-792 ; q6_tuned ms.jl:317-325 — L 14, T 211, U 4, X 0
* `k6|natural|q1` (entrée `q1_natural`) : q1_natural ms.jl:326-334 — L 9, T 143, U 0, X 0
* `k6|natural|q6` (entrée `q6_natural`) : q6_natural ms.jl:308-316 — L 9, T 92, U 0, X 0
* `k6|tuned_v|q1` (entrée `q1_tuned_v`) : q1_tuned_v ms.jl:445-779 ; q1_natural ms.jl:326-334 — L 344, T 5772, U 324, X 0
* `k6|tuned_v|q6` (entrée `q6_tuned_v`) : q6_tuned_v ms.jl:388-440 ; q6_natural ms.jl:308-316 — L 62, T 1028, U 46, X 0
* `k7|natural|` (entrée `Dict`) : k7_natural ms.jl:826-831 — L 6, T 68, U 0, X 0
* `k7|tuned_pf|` (entrée `prefetchw`) : slot ms.jl:814-816 ; k7_tuned_pf ms.jl:819-819, ms.jl:839-839, ms.jl:841-859 — L 24, T 252, U 18, X 0
* `k7|tuned|` (entrée `Slot`) : slot ms.jl:814-816 ; k7_tuned ms.jl:867-867, ms.jl:869-878 — L 14, T 133, U 9, X 0
* `k8|natural|` (entrée `t_build`) : k8_natural ms.jl:891-901 — L 11, T 133, U 0, X 0
* `k8|tuned_it|` (entrée `a_build_it`) : k8_tuned_it ms.jl:902-904, ms.jl:947-975, ms.jl:982-984 — L 35, T 373, U 22, X 0
* `k9|mt_pool_v|` (entrée `k9_cols_v`) : k9_mt_pool_v ms.jl:1124-1125 ; k9_tuned_v ms.jl:1025-1090 — L 68, T 845, U 65, X 0
* `k9|mt|` (entrée `k9_cols`) : k9_mt ms.jl:1127-1128 ; k9_cols ms.jl:1097-1103 — L 9, T 147, U 5, X 0
* `k9|natural|` (entrée `k9_natural`) : k9_natural ms.jl:1092-1096 — L 5, T 87, U 0, X 0
* `k9|tuned_v|` (entrée `k9_cols_v`) : k9_tuned_v ms.jl:1025-1090 — L 66, T 794, U 65, X 0
* `k9|tuned|` (entrée `k9_cols`) : k9_cols ms.jl:1097-1103 — L 7, T 94, U 5, X 0

## mojo

* `k1|natural|energy` (entrée `k1_natural`) : k1_natural ms.mojo:66-71 — L 6, T 69, U 0, X 0
* `k1|soa|energy` (entrée `k1_soa`) : k1_soa ms.mojo:83-96, ms.mojo:127-132 — L 20, T 339, U 6, X 0
* `k3|sw_packed|` (entrée `k3_worker`) : k3 ms.mojo:174-181, ms.mojo:184-185, ms.mojo:187-187, ms.mojo:192-196 — L 16, T 225, U 2, X 0
* `k3|sw_padded|` (entrée `k3_worker`) : k3 ms.mojo:174-181, ms.mojo:184-185, ms.mojo:187-187, ms.mojo:192-196 — L 16, T 225, U 2, X 0
* `k4|natural_unsorted|` (entrée `k4_natural`) : k4_natural ms.mojo:205-211 — L 7, T 43, U 0, X 0
* `k4|tuned|` (entrée `k4_tuned`) : k4_tuned ms.mojo:223-240 — L 18, T 171, U 3, X 0
* `k5|natural|` (entrée `k5_natural`) : k5_natural ms.mojo:288-293 — L 6, T 59, U 0, X 0
* `k5|tuned|` (entrée `k5_tuned`) : k5_tuned ms.mojo:295-306 — L 12, T 268, U 4, X 0
* `k6|mt_pool_v|q1` (entrée `k6_worker_v`) : k6_worker_v ms.mojo:461-464, ms.mojo:488-492 ; fold ms.mojo:453-457 ; q1_tuned_v ms.mojo:416-451 ; simd_i ms.mojo:343-343, ms.mojo:345-347 ; q1_natural ms.mojo:362-373 — L 66, T 935, U 3, X 0
* `k6|mt|q6` (entrée `k6_worker`) : k6_worker ms.mojo:466-471, ms.mojo:482-486 ; q6_tuned ms.mojo:349-360 ; simd_i ms.mojo:343-343, ms.mojo:345-347 ; q6_natural ms.mojo:335-341 — L 34, T 552, U 3, X 0
* `k6|natural|q1` (entrée `q1_natural`) : q1_natural ms.mojo:362-373 — L 12, T 168, U 0, X 0
* `k6|natural|q6` (entrée `q6_natural`) : q6_natural ms.mojo:335-341 — L 7, T 109, U 0, X 0
* `k6|tuned_v|q1` (entrée `q1_tuned_v`) : q1_tuned_v ms.mojo:416-451 ; simd_i ms.mojo:343-343, ms.mojo:345-347 ; q1_natural ms.mojo:362-373 — L 52, T 755, U 3, X 0
* `k6|tuned|q6` (entrée `q6_tuned`) : q6_tuned ms.mojo:349-360 ; simd_i ms.mojo:343-343, ms.mojo:345-347 ; q6_natural ms.mojo:335-341 — L 23, T 377, U 3, X 0
* `k7|natural|` (entrée `Agg`) : k7_natural ms.mojo:509-512, ms.mojo:529-537 — L 13, T 108, U 0, X 0
* `k7|tuned|` (entrée `Slot`) : k7_tuned ms.mojo:514-518, ms.mojo:543-544, ms.mojo:546-562 — L 24, T 268, U 7, X 0
* `k8|natural|` (entrée `t_build`) : k8_natural ms.mojo:575-607 — L 30, T 277, U 9, X 0
* `k8|tuned_val|` (entrée `av_build`) : k8_tuned_val ms.mojo:609-613, ms.mojo:626-630, ms.mojo:635-643, ms.mojo:706-706 — L 20, T 221, U 7, X 0
* `k9|mt|` (entrée `k9_worker`) : k9_mt ms.mojo:771-773, ms.mojo:841-845 ; k9_rows ms.mojo:754-769, ms.mojo:828-829 — L 26, T 487, U 7, X 0
* `k9|natural|` (entrée `k9_natural`) : k9_natural ms.mojo:741-745, ms.mojo:778-784 — L 12, T 176, U 0, X 0
* `k9|tuned|` (entrée `k9_rows`) : k9_rows ms.mojo:754-769, ms.mojo:828-829 — L 18, T 295, U 6, X 0

## csharp

* `k1|natural|energy` (entrée `K1Natural`) : k1_natural Program.cs:44-47, Program.cs:52-58, Program.cs:126-131 — L 17, T 293, U 0, X 0
* `k1|soa|energy` (entrée `K1SoA`) : k1_soa Program.cs:75-90, Program.cs:115-120 — L 22, T 259, U 17, X 0
* `k3|sw_packed|` (entrée `Thread`) : k3 Program.cs:172-173, Program.cs:175-175, Program.cs:178-181, Program.cs:183-190 — L 15, T 174, U 0, X 0
* `k3|sw_padded|` (entrée `Thread`) : k3 Program.cs:172-173, Program.cs:175-175, Program.cs:178-181, Program.cs:183-190 — L 15, T 174, U 0, X 0
* `k4|natural_unsorted|` (entrée `K4Natural`) : k4_natural Program.cs:198-199 — L 2, T 44, U 0, X 0
* `k4|tuned|` (entrée `K4Tuned`) : k4_tuned Program.cs:205-223 — L 19, T 240, U 1, X 2
* `k5|natural|` (entrée `K5Natural`) : k5_natural Program.cs:262-263 — L 2, T 60, U 0, X 0
* `k5|tuned|` (entrée `K5Tuned`) : k5_tuned Program.cs:264-276, Program.cs:280-280 ; load_aligned Program.cs:18-25 — L 22, T 318, U 21, X 0
* `k6|mt_pool|q6` (entrée `Parallel`) : k6_mt_pool Program.cs:389-396 ; q6_tuned Program.cs:303-319 ; ld Program.cs:301-302 ; q6_natural Program.cs:293-300 — L 35, T 469, U 2, X 1
* `k6|mt|q1` (entrée `Thread`) : k6_mt Program.cs:400-413 ; q1_tuned Program.cs:334-375 ; ld Program.cs:301-302 ; q1_natural Program.cs:320-332 — L 71, T 999, U 5, X 3
* `k6|natural|q1` (entrée `Q1Natural`) : q1_natural Program.cs:320-332 — L 13, T 153, U 0, X 0
* `k6|natural|q6` (entrée `Q6Natural`) : q6_natural Program.cs:293-300 — L 8, T 94, U 0, X 0
* `k6|tuned|q1` (entrée `Q1Tuned`) : q1_tuned Program.cs:334-375 ; ld Program.cs:301-302 ; q1_natural Program.cs:320-332 — L 57, T 847, U 5, X 3
* `k6|tuned|q6` (entrée `Q6Tuned`) : q6_tuned Program.cs:303-319 ; ld Program.cs:301-302 ; q6_natural Program.cs:293-300 — L 27, T 369, U 2, X 1
* `k7|natural|` (entrée `Dictionary`) : k7_natural Program.cs:437-442 — L 6, T 87, U 0, X 0
* `k7|tuned|` (entrée `Slot`) : k7_tuned Program.cs:427-427, Program.cs:449-449, Program.cs:451-465 — L 17, T 239, U 14, X 1
* `k8|natural|` (entrée `TBuild`) : k8_natural Program.cs:474-474, Program.cs:476-477 — L 3, T 101, U 0, X 0
* `k8|tuned_it|` (entrée `ABuildIt`) : k8_tuned_it Program.cs:478-479, Program.cs:506-543, Program.cs:551-551 — L 41, T 406, U 2, X 0
* `k9|mt_pool|` (entrée `Parallel`) : k9_mt_pool Program.cs:632-633 ; k9_rows Program.cs:588-600, Program.cs:605-605, Program.cs:607-607 — L 17, T 329, U 15, X 0
* `k9|natural|` (entrée `K9Natural`) : k9_natural Program.cs:580-586, Program.cs:604-604, Program.cs:606-606 — L 9, T 149, U 0, X 0
* `k9|tuned|` (entrée `K9Rows`) : k9_rows Program.cs:588-600, Program.cs:605-605, Program.cs:607-607 — L 15, T 273, U 14, X 0

## fpc

* `k1|natural|energy` (entrée `K1Natural`) : k1_natural ms.pas:156-165 — L 10, T 98, U 0, X 0
* `k1|soa|energy` (entrée `K1SoAV`) : k1_soa ms.pas:238-238, ms.pas:266-271, msvec.pas:20-20, msvec.pas:27-44 ; msvec_unit msvec.pas:8-8, msvec.pas:10-12, msvec.pas:14-14, msvec.pas:16-18, msvec.pas:24-24, msvec.pas:100-100 ; aligned ms.pas:44-51 — L 44, T 393, U 1, X 0
* `k3|sw_packed|` (entrée `K3Worker`) : k3 ms.pas:357-362, ms.pas:366-379, ms.pas:383-384, ms.pas:386-387, ms.pas:392-395, ms.pas:405-412 ; aligned ms.pas:44-51 — L 44, T 299, U 3, X 0
* `k3|sw_padded|` (entrée `K3Worker`) : k3 ms.pas:357-362, ms.pas:366-379, ms.pas:383-384, ms.pas:386-387, ms.pas:392-395, ms.pas:405-412 ; aligned ms.pas:44-51 — L 44, T 299, U 3, X 0
* `k4|natural_unsorted|` (entrée `K4Natural`) : k4_natural ms.pas:426-436 — L 11, T 58, U 0, X 0
* `k4|swar|` (entrée `K4Swar`) : k4_swar ms.pas:476-512 — L 37, T 252, U 0, X 0
* `k5|natural|` (entrée `K5Natural`) : k5_natural ms.pas:559-568 — L 10, T 57, U 0, X 0
* `k5|tuned_v|` (entrée `K5TunedVPtr`) : k5_tuned_v ms.pas:597-597, ms.pas:610-611, msvec.pas:22-22, msvec.pas:75-98 ; msvec_unit msvec.pas:8-8, msvec.pas:10-12, msvec.pas:14-14, msvec.pas:16-18, msvec.pas:24-24, msvec.pas:100-100 ; load_raw ms.pas:103-110 ; aligned ms.pas:44-51 — L 54, T 473, U 1, X 0
* `k6|mt_pool|q1` (entrée `K6PoolJob`) : k6_pool ms.pas:930-938, ms.pas:941-956, ms.pas:975-975, ms.pas:1017-1018, ms.pas:1026-1036, ms.pas:1069-1070 ; pool ms.pas:643-651, ms.pas:653-654, ms.pas:656-670, ms.pas:672-684, ms.pas:686-697, ms.pas:699-712 ; q1_tuned ms.pas:789-847 ; q1_sum ms.pas:958-965 ; colsp ms.pas:729-733, ms.pas:970-970, ms.pas:1010-1016 ; load_raw ms.pas:103-110 ; aligned ms.pas:44-51 — L 201, T 1602, U 8, X 0
* `k6|mt_pool|q6` (entrée `K6PoolJob`) : k6_pool ms.pas:930-938, ms.pas:941-956, ms.pas:975-975, ms.pas:1017-1018, ms.pas:1026-1036, ms.pas:1069-1070 ; pool ms.pas:643-651, ms.pas:653-654, ms.pas:656-670, ms.pas:672-684, ms.pas:686-697, ms.pas:699-712 ; q6_tuned ms.pas:770-783 ; colsp ms.pas:729-733, ms.pas:970-970, ms.pas:1010-1016 ; load_raw ms.pas:103-110 ; aligned ms.pas:44-51 — L 148, T 992, U 8, X 0
* `k6|mt|q1` (entrée `K6Worker`) : k6_mt ms.pas:907-915, ms.pas:917-928, ms.pas:973-974, ms.pas:1040-1055 ; q1_tuned ms.pas:789-847 ; q1_sum ms.pas:958-965 ; colsp ms.pas:729-733, ms.pas:970-970, ms.pas:1010-1016 ; load_raw ms.pas:103-110 ; aligned ms.pas:44-51 — L 135, T 1252, U 6, X 0
* `k6|natural|q1` (entrée `Q1Natural`) : q1_natural ms.pas:747-765 — L 19, T 189, U 0, X 0
* `k6|natural|q6` (entrée `Q6Natural`) : q6_natural ms.pas:735-745 — L 11, T 120, U 0, X 0
* `k6|tuned|q1` (entrée `Q1Tuned`) : q1_tuned ms.pas:789-847 ; colsp ms.pas:729-733, ms.pas:970-970, ms.pas:1010-1016 ; load_raw ms.pas:103-110 ; aligned ms.pas:44-51 — L 88, T 892, U 1, X 0
* `k6|tuned|q6` (entrée `Q6Tuned`) : q6_tuned ms.pas:770-783 ; colsp ms.pas:729-733, ms.pas:970-970, ms.pas:1010-1016 ; load_raw ms.pas:103-110 ; aligned ms.pas:44-51 — L 43, T 351, U 1, X 0
* `k7|natural|` (entrée `TAggMap`) : k7_natural ms.pas:1081-1084, ms.pas:1086-1086, ms.pas:1174-1174, ms.pas:1176-1176, ms.pas:1198-1206 — L 16, T 102, U 0, X 0
* `k7|tuned|` (entrée `K7Tuned`) : k7_tuned ms.pas:1076-1078, ms.pas:1088-1092, ms.pas:1097-1128, ms.pas:1177-1177 ; aligned ms.pas:44-51 — L 49, T 362, U 2, X 0
* `k8|natural|` (entrée `TBuild`) : k8_natural ms.pas:1236-1240, ms.pas:1249-1285 — L 40, T 192, U 9, X 0
* `k8|tuned_it|` (entrée `AIBuild`) : k8_tuned_it ms.pas:1242-1246, ms.pas:1346-1419, ms.pas:1473-1473, ms.pas:1489-1489 — L 80, T 436, U 1, X 0
* `k9|mt_pool|` (entrée `K9PoolJob`) : k9_pool ms.pas:1641-1646, ms.pas:1655-1658, ms.pas:1666-1666, ms.pas:1713-1714, ms.pas:1728-1730, ms.pas:1756-1757 ; pool ms.pas:643-651, ms.pas:653-654, ms.pas:656-670, ms.pas:672-684, ms.pas:686-697, ms.pas:699-712 ; k9_rows ms.pas:1617-1639, ms.pas:1663-1663, ms.pas:1709-1711 ; aligned ms.pas:44-51 — L 118, T 752, U 1, X 0
* `k9|natural|` (entrée `K9Natural`) : k9_natural ms.pas:1550-1550, ms.pas:1552-1553, ms.pas:1555-1562, ms.pas:1662-1662, ms.pas:1683-1684 — L 14, T 132, U 1, X 0
* `k9|tuned|` (entrée `K9Rows`) : k9_rows ms.pas:1617-1639, ms.pas:1663-1663, ms.pas:1709-1711 ; aligned ms.pas:44-51 — L 35, T 278, U 0, X 0

## java

* `k1|natural|energy` (entrée `k1Natural`) : k1_natural Ms.java:86-87, Ms.java:89-93, Ms.java:161-166 — L 13, T 282, U 0, X 0
* `k1|soa|energy` (entrée `k1SoASeg`) : k1_soa Ms.java:118-131, Ms.java:153-155 ; fs Ms.java:67-67 ; ds Ms.java:68-68 ; no Ms.java:76-76 — L 20, T 377, U 0, X 0
* `k3|sw_packed|` (entrée `LA`) : k3 Ms.java:195-195, Ms.java:197-198, Ms.java:200-201, Ms.java:203-205, Ms.java:207-212, Ms.java:214-214 — L 15, T 230, U 0, X 0
* `k3|sw_padded|` (entrée `LA`) : k3 Ms.java:195-195, Ms.java:197-198, Ms.java:200-201, Ms.java:203-205, Ms.java:207-212, Ms.java:214-214 — L 15, T 230, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4Natural`) : k4_natural Ms.java:221-221 — L 1, T 45, U 0, X 0
* `k4|tuned|` (entrée `k4Tuned`) : k4_tuned Ms.java:227-247 ; is Ms.java:69-69 — L 22, T 308, U 0, X 0
* `k5|natural|` (entrée `k5Natural`) : k5_natural Ms.java:286-286 — L 1, T 52, U 0, X 0
* `k5|tuned|` (entrée `k5TunedSeg`) : k5_tuned Ms.java:297-307, Ms.java:315-315 ; fs Ms.java:67-67 ; no Ms.java:76-76 ; aligned Ms.java:77-81 — L 19, T 323, U 0, X 0
* `k6|mt_pool_v|q1` (entrée `q1OnePass`) : k6_pool Ms.java:471-471, Ms.java:475-481, Ms.java:502-502 ; pool Ms.java:51-65 ; q1_onepass Ms.java:402-464 ; is Ms.java:69-69 ; ls_bs Ms.java:70-71 ; q1_natural Ms.java:348-356 — L 99, T 2366, U 0, X 0
* `k6|mt_pool|q6` (entrée `poolRun`) : k6_pool Ms.java:471-471, Ms.java:475-481, Ms.java:502-502 ; pool Ms.java:51-65 ; q6_tuned Ms.java:334-347 ; is Ms.java:69-69 ; ls_bs Ms.java:70-71 ; q6_natural Ms.java:328-333 — L 47, T 729, U 0, X 0
* `k6|mt|q6` (entrée `q6Tuned`) : k6_mt Ms.java:483-494 ; q6_tuned Ms.java:334-347 ; is Ms.java:69-69 ; ls_bs Ms.java:70-71 ; q6_natural Ms.java:328-333 — L 35, T 581, U 0, X 0
* `k6|natural|q1` (entrée `q1Natural`) : q1_natural Ms.java:348-356 — L 9, T 145, U 0, X 0
* `k6|natural|q6` (entrée `q6Natural`) : q6_natural Ms.java:328-333 — L 6, T 86, U 0, X 0
* `k6|tuned_v|q1` (entrée `q1OnePass`) : q1_onepass Ms.java:402-464 ; is Ms.java:69-69 ; ls_bs Ms.java:70-71 ; q1_natural Ms.java:348-356 — L 75, T 2034, U 0, X 0
* `k6|tuned|q6` (entrée `q6Tuned`) : q6_tuned Ms.java:334-347 ; is Ms.java:69-69 ; ls_bs Ms.java:70-71 ; q6_natural Ms.java:328-333 — L 23, T 397, U 0, X 0
* `k7|natural|` (entrée `HashMap`) : k7_natural Ms.java:506-506, Ms.java:530-534 — L 6, T 77, U 0, X 0
* `k7|rq_iso|` (entrée `k7TunedIso`) : k7_rq_iso Ms.java:511-523 — L 13, T 174, U 0, X 0
* `k8|natural|` (entrée `tBuild`) : k8_natural Ms.java:566-566, Ms.java:568-569 — L 3, T 104, U 0, X 0
* `k8|tuned_it|` (entrée `aBuildIt`) : k8_tuned_it Ms.java:571-571, Ms.java:595-622, Ms.java:629-629 — L 30, T 364, U 0, X 0
* `k9|mt_pool_v|` (entrée `k9RowsVec`) : k9_pool Ms.java:697-697, Ms.java:722-726, Ms.java:744-744 ; pool Ms.java:51-65 ; k9_vec Ms.java:676-688 ; ds Ms.java:68-68 ; k9_flat Ms.java:692-692, Ms.java:694-694 — L 38, T 566, U 0, X 0
* `k9|mt_pool|` (entrée `poolRun`) : k9_pool Ms.java:697-697, Ms.java:722-726, Ms.java:744-744 ; pool Ms.java:51-65 ; k9_rows Ms.java:666-671 ; k9_flat Ms.java:692-692, Ms.java:694-694 — L 30, T 438, U 0, X 0
* `k9|natural|` (entrée `k9Natural`) : k9_natural Ms.java:655-659, Ms.java:691-691, Ms.java:693-693 — L 7, T 154, U 0, X 0

## go

* `k1|natural|energy` (entrée `k1Natural`) : k1_natural ms.go:69-76 — L 8, T 66, U 0, X 0
* `k1|soa|energy` (entrée `k1SoA`) : k1_soa ms.go:95-118, ms.go:168-175 — L 32, T 297, U 0, X 7
* `k3|rmw_packed|` (entrée `ctr`) : k3 ms.go:217-217, ms.go:225-227, ms.go:229-229, ms.go:231-232, ms.go:234-235, ms.go:237-251 ; k3_packed ms.go:223-223, ms.go:230-230 — L 26, T 139, U 0, X 0
* `k3|rmw_padded|` (entrée `padded`) : k3 ms.go:217-217, ms.go:225-227, ms.go:229-229, ms.go:231-232, ms.go:234-235, ms.go:237-251 ; k3_padded ms.go:211-214, ms.go:224-224, ms.go:228-228 — L 30, T 153, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4Natural`) : k4_natural ms.go:262-271 — L 10, T 44, U 0, X 0
* `k4|tuned|` (entrée `k4Tuned`) : k4_tuned ms.go:284-307 — L 24, T 157, U 0, X 4
* `k5|natural|` (entrée `k5Natural`) : k5_natural ms.go:359-366 — L 8, T 43, U 0, X 0
* `k5|tuned_v|` (entrée `k5TunedR`) : k5_tuned_v ms.go:393-414 — L 20, T 296, U 0, X 6
* `k5|tuned|` (entrée `k5Tuned`) : k5_tuned ms.go:368-386 — L 19, T 260, U 0, X 6
* `k6|mt_pool_v|q1` (entrée `q1OnePass`) : k6_mt ms.go:696-719 ; q1_onepass ms.go:536-641 ; sum3264 ms.go:643-661 ; q1_natural ms.go:483-497 ; fold ms.go:663-671 — L 172, T 2126, U 0, X 30
* `k6|mt|q1` (entrée `q1Tuned`) : k6_mt ms.go:696-719 ; q1_tuned ms.go:502-528 ; fold ms.go:663-671 — L 60, T 519, U 0, X 0
* `k6|mt|q6` (entrée `q6Tuned`) : k6_mt ms.go:696-719 ; q6_tuned ms.go:459-481 ; q6_natural ms.go:446-455 — L 57, T 554, U 0, X 8
* `k6|natural|q1` (entrée `q1Natural`) : q1_natural ms.go:483-497 — L 15, T 157, U 0, X 0
* `k6|natural|q6` (entrée `q6Natural`) : q6_natural ms.go:446-455 — L 10, T 108, U 0, X 0
* `k6|tuned|q1` (entrée `q1Tuned`) : q1_tuned ms.go:502-528 — L 27, T 336, U 0, X 0
* `k6|tuned|q6` (entrée `q6Tuned`) : q6_tuned ms.go:459-481 ; q6_natural ms.go:446-455 — L 33, T 412, U 0, X 8
* `k7|natural|` (entrée `agg`) : k7_natural ms.go:726-729, ms.go:743-749 — L 11, T 55, U 0, X 0
* `k7|tuned|` (entrée `slot`) : k7_tuned ms.go:730-733, ms.go:756-757, ms.go:759-769 — L 17, T 115, U 0, X 0
* `k8|natural|` (entrée `tBuild`) : k8_natural ms.go:785-788, ms.go:790-804 — L 19, T 107, U 0, X 0
* `k8|tuned_it|` (entrée `aBuildIt`) : k8_tuned_it ms.go:806-809, ms.go:850-850, ms.go:852-899, ms.go:909-909, ms.go:926-926 — L 55, T 317, U 0, X 0
* `k9|mt_pool_v|` (entrée `k9RowsVec`) : k9_mt ms.go:1070-1082 ; k9_vec ms.go:985-1008 ; k9_flat ms.go:1012-1012, ms.go:1019-1019 — L 39, T 518, U 0, X 8
* `k9|natural|` (entrée `k9Natural`) : k9_natural ms.go:949-956, ms.go:1011-1011, ms.go:1014-1017 — L 13, T 171, U 0, X 0
* `k9|tuned_v|` (entrée `k9RowsVec`) : k9_vec ms.go:985-1008 ; k9_flat ms.go:1012-1012, ms.go:1019-1019 — L 26, T 404, U 0, X 8

## haskell

* `k1|natural|energy` (entrée `k1Natural`) : k1_natural Ms.hs:73-73, Ms.hs:75-76, Ms.hs:142-145, Ms.hs:223-223 — L 8, T 190, U 1, X 0
* `k1|soa|energy` (entrée `k1SoA`) : k1_soa Ms.hs:93-109, Ms.hs:133-138 — L 23, T 375, U 8, X 0
* `k3|rmw_packed|` (entrée `fetchAddI`) : k3 Ms.hs:179-179, Ms.hs:181-182, Ms.hs:184-184, Ms.hs:186-186, Ms.hs:205-206, Ms.hs:208-211, Ms.hs:214-214, Ms.hs:217-217 ; parallel_io Ms.hs:195-201 — L 20, T 303, U 0, X 0
* `k3|rmw_padded|` (entrée `fetchAddI`) : k3 Ms.hs:179-179, Ms.hs:181-182, Ms.hs:184-184, Ms.hs:186-186, Ms.hs:205-206, Ms.hs:208-211, Ms.hs:214-214, Ms.hs:217-217 ; parallel_io Ms.hs:195-201 — L 20, T 303, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4Natural`) : k4_natural Ms.hs:221-221, Ms.hs:226-227 — L 3, T 36, U 0, X 0
* `k4|tuned|` (entrée `k4TunedAddr`) : k4_tuned Ms.hs:236-238, Ms.hs:240-271 — L 33, T 615, U 3, X 0
* `k5|natural|` (entrée `k5Natural`) : k5_natural Ms.hs:224-224, Ms.hs:324-325, Ms.hs:356-359 — L 7, T 117, U 2, X 0
* `k5|tuned|` (entrée `k5Tuned`) : k5_tuned Ms.hs:327-342 — L 15, T 303, U 3, X 0
* `k6|mt|q1` (entrée `forkOn`) : k6_mt Ms.hs:477-478 ; one Ms.hs:473-473 ; q1_tuned Ms.hs:420-437 — L 21, T 326, U 3, X 0
* `k6|mt|q6` (entrée `forkOn`) : k6_mt Ms.hs:477-478 ; one Ms.hs:473-473 ; q6_tuned Ms.hs:389-397 — L 12, T 205, U 0, X 0
* `k6|natural|q1` (entrée `q1Natural`) : q1_natural Ms.hs:401-417 — L 17, T 235, U 3, X 0
* `k6|natural|q6` (entrée `q6Natural`) : q6_natural Ms.hs:377-386 — L 10, T 113, U 0, X 0
* `k6|tuned|q1` (entrée `q1Tuned`) : one Ms.hs:473-473 ; q1_tuned Ms.hs:420-437 — L 19, T 269, U 3, X 0
* `k6|tuned|q6` (entrée `q6Tuned`) : one Ms.hs:473-473 ; q6_tuned Ms.hs:389-397 — L 10, T 148, U 0, X 0
* `k7|natural|` (entrée `insertWith`) : k7_natural Ms.hs:547-553 — L 7, T 85, U 2, X 0
* `k7|tuned_pf|` (entrée `k7TunedPf`) : k7_params Ms.hs:557-557 ; k7_tuned_pf Ms.hs:492-534 — L 44, T 487, U 14, X 0
* `k7|tuned|` (entrée `probe`) : k7_params Ms.hs:557-557 ; k7_tuned Ms.hs:559-580 — L 23, T 231, U 10, X 0
* `k8|natural|` (entrée `tBuild`) : k8_natural Ms.hs:591-591, Ms.hs:593-595, Ms.hs:597-599 — L 7, T 104, U 0, X 0
* `k8|tuned_it|` (entrée `aBuildIt`) : k8_tuned_it Ms.hs:645-668, Ms.hs:670-686, Ms.hs:693-693, Ms.hs:695-698 — L 46, T 446, U 19, X 0
* `k9|mt|` (entrée `parallelIO`) : k9_mt Ms.hs:774-774 ; parallel_io Ms.hs:195-201 ; k9_rows Ms.hs:733-753, Ms.hs:768-770 — L 32, T 471, U 10, X 0
* `k9|natural|` (entrée `k9Step`) : k9_natural Ms.hs:225-225, Ms.hs:726-730, Ms.hs:760-761 — L 8, T 203, U 0, X 0
* `k9|tuned|` (entrée `k9Rows`) : k9_rows Ms.hs:733-753, Ms.hs:768-770 — L 24, T 367, U 10, X 0

## ocaml

* `k1|natural|energy` (entrée `k1_natural`) : k1_natural ms.ml:32-33, ms.ml:35-38, ms.ml:94-94, ms.ml:96-98 — L 10, T 273, U 0, X 0
* `k1|soa|energy` (entrée `k1_soa`) : k1_soa ms.ml:54-54, ms.ml:57-68, ms.ml:90-91 — L 15, T 266, U 3, X 0
* `k3|rmw_packed|` (entrée `fetch_and_add`) : k3 ms.ml:131-131, ms.ml:135-141 — L 8, T 120, U 0, X 0
* `k3|rmw_padded|` (entrée `make_contended`) : k3 ms.ml:131-131, ms.ml:135-141 — L 8, T 120, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4_natural`) : k4_natural ms.ml:145-151 — L 7, T 62, U 1, X 0
* `k4|swar|` (entrée `k4_swar`) : k4_swar ms.ml:192-214 — L 23, T 253, U 1, X 0
* `k4|tuned|` (entrée `k4_tuned`) : k4_tuned ms.ml:165-183 — L 19, T 192, U 1, X 0
* `k5|natural|` (entrée `k5_natural`) : k5_natural ms.ml:233-236 — L 4, T 76, U 0, X 0
* `k5|tuned|` (entrée `k5_tuned`) : k5_tuned ms.ml:238-246 — L 9, T 153, U 1, X 0
* `k6|mt_pool_s|q6` (entrée `pool_run`) : k6_pool ms.ml:420-420, ms.ml:425-429, ms.ml:436-436 ; pool ms.ml:263-263, ms.ml:265-265, ms.ml:267-277, ms.ml:279-279, ms.ml:281-281, ms.ml:283-306 ; one_s ms.ml:418-418 ; q6_tuned_m ms.ml:365-372 — L 53, T 587, U 2, X 0
* `k6|mt|q1` (entrée `q1_tuned`) : k6_mt ms.ml:432-433 ; q1_tuned ms.ml:346-359 — L 16, T 349, U 9, X 0
* `k6|natural|q1` (entrée `q1_natural`) : q1_natural ms.ml:335-343 — L 9, T 205, U 0, X 0
* `k6|natural|q6` (entrée `q6_natural`) : q6_natural ms.ml:316-322 — L 7, T 108, U 0, X 0
* `k6|tuned_s|q6` (entrée `q6_tuned_m`) : one_s ms.ml:418-418 ; q6_tuned_m ms.ml:365-372 — L 9, T 173, U 2, X 0
* `k6|tuned|q1` (entrée `q1_tuned`) : q1_tuned ms.ml:346-359 — L 14, T 290, U 9, X 0
* `k7|natural|` (entrée `Hashtbl`) : k7_natural ms.ml:439-439, ms.ml:449-455 — L 8, T 97, U 0, X 0
* `k7|tuned_oa|` (entrée `cmask`) : k7_tuned_oa ms.ml:464-466, ms.ml:468-476 — L 12, T 195, U 3, X 0
* `k8|natural|` (entrée `t_build`) : k8_natural ms.ml:511-511, ms.ml:513-517, ms.ml:519-519 — L 7, T 109, U 0, X 0
* `k8|tuned_it|` (entrée `a_build_it`) : k8_tuned_it ms.ml:522-522, ms.ml:556-556, ms.ml:558-599, ms.ml:608-608 — L 44, T 358, U 14, X 0
* `k9|mt_pool|` (entrée `pool_run`) : k9_pool ms.ml:688-688, ms.ml:691-691, ms.ml:703-703 ; pool ms.ml:263-263, ms.ml:265-265, ms.ml:267-277, ms.ml:279-279, ms.ml:281-281, ms.ml:283-306 ; k9_rows ms.ml:651-658, ms.ml:686-686 — L 49, T 569, U 2, X 0
* `k9|natural|` (entrée `k9_natural`) : k9_natural ms.ml:636-639, ms.ml:663-663 — L 5, T 126, U 0, X 0
* `k9|tuned|` (entrée `k9_rows`) : k9_rows ms.ml:651-658, ms.ml:686-686 — L 9, T 174, U 2, X 0

## bqn

* `k1|natural|energy` (entrée `K1Nat`) : k1_natural ms.bqn:44-45 — L 2, T 53, U 0, X 0
* `k1|soa|energy` (entrée `K1Tun`) : k1_soa ms.bqn:46-46, ms.bqn:64-64 — L 2, T 51, U 0, X 0
* `k3|rmw_packed|` (entrée `stride`) : k3 ms.bqn:107-107, ms.bqn:109-110 — L 3, T 49, U 0, X 0
* `k3|rmw_padded|` (entrée `stride`) : k3 ms.bqn:107-107, ms.bqn:109-110 — L 3, T 49, U 0, X 0
* `k3|sw_packed|` (entrée `stride`) : k3 ms.bqn:107-107, ms.bqn:109-110 — L 3, T 49, U 0, X 0
* `k3|sw_padded|` (entrée `stride`) : k3 ms.bqn:107-107, ms.bqn:109-110 — L 3, T 49, U 0, X 0
* `k4|natural_unsorted|` (entrée `d`) : k4_natural ms.bqn:120-120 — L 1, T 18, U 0, X 0
* `k5|natural|` (entrée `b`) : k5_natural ms.bqn:128-128 — L 1, T 31, U 0, X 0
* `k5|tuned|` (entrée `Sum`) : k5_tuned ms.bqn:127-127 — L 1, T 36, U 0, X 0
* `k6|mt|q1` (entrée `Chunks`) : chunks ms.bqn:173-173 ; k6_mt_q1 ms.bqn:190-191 ; q1_tuned ms.bqn:144-150 — L 10, T 126, U 0, X 0
* `k6|mt|q6` (entrée `Chunks`) : chunks ms.bqn:173-173 ; k6_mt_q6 ms.bqn:184-185 ; q6_tuned ms.bqn:134-134 — L 4, T 87, U 0, X 0
* `k6|natural|q1` (entrée `Q1Nat`) : q1_natural ms.bqn:135-143 — L 9, T 99, U 0, X 0
* `k6|natural|q6` (entrée `Q6Nat`) : q6_natural ms.bqn:133-133 — L 1, T 48, U 0, X 0
* `k6|tuned|q1` (entrée `Q1Tun`) : q1_tuned ms.bqn:144-150 — L 7, T 92, U 0, X 0
* `k6|tuned|q6` (entrée `Q6Tun`) : q6_tuned ms.bqn:134-134 — L 1, T 54, U 0, X 0
* `k7|natural|` (entrée `keys`) : k7_natural ms.bqn:212-213 — L 2, T 29, U 0, X 0
* `k7|tuned|` (entrée `ki`) : k7_tuned ms.bqn:218-218, ms.bqn:221-227 — L 8, T 62, U 0, X 0
* `k8|natural|` (entrée `Build`) : k8_natural ms.bqn:239-241 — L 3, T 103, U 0, X 0
* `k8|tuned|` (entrée `ABuild`) : k8_tuned ms.bqn:248-258 — L 11, T 180, U 0, X 0
* `k9|mt|` (entrée `J9Tun`) : k9_tuned ms.bqn:324-330, ms.bqn:331-331 — L 8, T 121, U 0, X 0
* `k9|natural|` (entrée `J9Nat`) : k9_natural ms.bqn:319-323 — L 5, T 78, U 0, X 0
* `k9|tuned|` (entrée `J9Tun`) : k9_tuned ms.bqn:324-330, ms.bqn:331-331 — L 8, T 121, U 0, X 0

## php

* `k1|natural|energy` (entrée `k1_natural`) : k1_natural ms.php:102-112, ms.php:117-124, ms.php:209-213 — L 24, T 229, U 0, X 0
* `k1|soa|energy` (entrée `k1_soa`) : k1_soa ms.php:135-146, ms.php:185-185, ms.php:187-194, ms.php:196-199 — L 25, T 253, U 0, X 0
* `k3|sw_packed|` (entrée `shmop_write`) : k3 ms.php:262-263, ms.php:268-292, ms.php:298-298, ms.php:300-300, ms.php:302-302 ; workers ms.php:54-76, ms.php:78-88, ms.php:90-97 — L 72, T 622, U 0, X 0
* `k3|sw_padded|` (entrée `shmop_write`) : k3 ms.php:262-263, ms.php:268-292, ms.php:298-298, ms.php:300-300, ms.php:302-302 ; workers ms.php:54-76, ms.php:78-88, ms.php:90-97 — L 72, T 622, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4_natural`) : k4_natural ms.php:317-326 — L 10, T 45, U 0, X 0
* `k4|tuned|` (entrée `k4_tuned`) : k4_tuned ms.php:340-349 — L 10, T 56, U 0, X 0
* `k5|natural|` (entrée `k5_natural`) : k5_natural ms.php:404-412 — L 9, T 69, U 0, X 0
* `k5|tuned|` (entrée `k5_tuned`) : k5_tuned ms.php:414-423 — L 10, T 97, U 0, X 0
* `k6|mt_pool_s|q6` (entrée `k6_mt`) : k6_mt_fn ms.php:571-574 ; k6_mt_pool_s ms.php:583-587, ms.php:589-589 ; workers ms.php:54-76, ms.php:78-88, ms.php:90-97 ; q6_tuned_s ms.php:484-493 — L 62, T 592, U 0, X 0
* `k6|mt|q1` (entrée `k6_mt`) : k6_mt_fn ms.php:571-574 ; k6_mt ms.php:602-606, ms.php:608-608 ; workers ms.php:54-76, ms.php:78-88, ms.php:90-97 ; q1_tuned ms.php:512-530 — L 70, T 696, U 0, X 0
* `k6|natural|q1` (entrée `q1_natural`) : q1_natural ms.php:495-510 — L 16, T 202, U 0, X 0
* `k6|natural|q6` (entrée `q6_natural`) : q6_natural ms.php:454-463 — L 10, T 126, U 0, X 0
* `k6|tuned_s|q6` (entrée `q6_tuned_s`) : q6_tuned_s ms.php:484-493 — L 10, T 142, U 0, X 0
* `k6|tuned|q1` (entrée `q1_tuned`) : q1_tuned ms.php:512-530 — L 18, T 246, U 0, X 0
* `k7|natural|` (entrée `isset`) : k7_natural ms.php:632-640 — L 9, T 81, U 0, X 0
* `k7|tuned_oa|` (entrée `array_fill`) : k7_tuned_oa ms.php:656-677 — L 22, T 232, U 0, X 0
* `k8|natural|` (entrée `t_build`) : k8_natural ms.php:733-738, ms.php:745-758 — L 19, T 137, U 0, X 0
* `k8|tuned|` (entrée `a_build`) : k8_tuned ms.php:763-818, ms.php:853-856 — L 59, T 422, U 0, X 0
* `k9|mt|` (entrée `run_workers`) : k9_mt ms.php:1009-1013, ms.php:1015-1063, ms.php:1068-1068, ms.php:1070-1070, ms.php:1088-1088 ; workers ms.php:54-76, ms.php:78-88, ms.php:90-97 ; k9_rows ms.php:914-922 — L 107, T 1146, U 0, X 0
* `k9|natural|` (entrée `k9_natural`) : k9_natural ms.php:894-901, ms.php:928-939 — L 20, T 240, U 0, X 0
* `k9|tuned|` (entrée `k9_rows`) : k9_rows ms.php:914-922 ; k9_flat ms.php:968-973 — L 15, T 199, U 0, X 0

## js

* `k1|natural|energy` (entrée `k1Natural`) : k1_natural ms.js:33-37, ms.js:75-80 — L 11, T 234, U 0, X 0
* `k1|soa|energy` (entrée `k1SoA`) : k1_soa ms.js:48-57, ms.js:71-71 — L 11, T 330, U 0, X 0
* `k3|rmw_packed|` (entrée `Atomics`) : k3 ms.js:114-114, ms.js:116-117, ms.js:120-121, ms.js:123-123, ms.js:125-125, ms.js:518-522 ; workers ms.js:104-109, ms.js:511-512, ms.js:517-517, ms.js:549-550, ms.js:568-568 — L 24, T 344, U 0, X 0
* `k3|rmw_padded|` (entrée `Atomics`) : k3 ms.js:114-114, ms.js:116-117, ms.js:120-121, ms.js:123-123, ms.js:125-125, ms.js:518-522 ; workers ms.js:104-109, ms.js:511-512, ms.js:517-517, ms.js:549-550, ms.js:568-568 — L 24, T 344, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4Natural`) : k4_natural ms.js:132-132 — L 1, T 51, U 0, X 0
* `k4|tuned|` (entrée `k4Tuned`) : k4_tuned ms.js:138-153, ms.js:158-159 — L 18, T 212, U 0, X 0
* `k5|natural|` (entrée `k5Natural`) : k5_natural ms.js:165-165 — L 1, T 45, U 0, X 0
* `k5|rq_f64|` (entrée `Float64Array`) : k5_rq_f64 ms.js:183-183 ; k5_tuned ms.js:166-173 — L 9, T 233, U 0, X 0
* `k5|tuned|` (entrée `k5Tuned`) : k5_tuned ms.js:166-173 — L 8, T 214, U 0, X 0
* `k6|mt_pool_s|q6` (entrée `q6TunedM`) : k6_mt ms.js:282-282, ms.js:294-298, ms.js:523-528 ; workers ms.js:104-109, ms.js:511-512, ms.js:517-517, ms.js:549-550, ms.js:568-568 ; load_shared ms.js:10-13 ; q6_tuned_m ms.js:217-228 — L 40, T 666, U 0, X 0
* `k6|mt|q1` (entrée `q1Tuned`) : k6_mt ms.js:282-282, ms.js:294-298, ms.js:523-528 ; workers ms.js:104-109, ms.js:511-512, ms.js:517-517, ms.js:549-550, ms.js:568-568 ; load_shared ms.js:10-13 ; q1_tuned ms.js:238-248 ; sum ms.js:277-277 — L 40, T 737, U 0, X 0
* `k6|natural|q1` (entrée `q1Natural`) : q1_natural ms.js:229-237 — L 9, T 153, U 0, X 0
* `k6|natural|q6` (entrée `q6Natural`) : q6_natural ms.js:200-204 — L 5, T 95, U 0, X 0
* `k6|tuned_s|q6` (entrée `q6TunedM`) : q6_tuned_m ms.js:217-228 — L 12, T 155, U 0, X 0
* `k7|natural|` (entrée `Map`) : k7_natural ms.js:308-312 — L 5, T 82, U 0, X 0
* `k7|tuned|` (entrée `tk`) : k7_tuned ms.js:316-316, ms.js:320-326 — L 8, T 152, U 0, X 0
* `k8|natural|` (entrée `tBuild`) : k8_natural ms.js:336-337 — L 2, T 89, U 0, X 0
* `k8|tuned_it|` (entrée `aBuildIt`) : k8_tuned_it ms.js:338-338, ms.js:354-371, ms.js:375-375 — L 20, T 357, U 0, X 0
* `k9|natural|` (entrée `k9Natural`) : k9_natural ms.js:400-403, ms.js:430-431 — L 6, T 157, U 0, X 0
* `k9|rq_slide_mt|` (entrée `k9RowsV`) : k9_mt ms.js:457-457, ms.js:459-459, ms.js:468-468, ms.js:475-475, ms.js:529-532 ; workers ms.js:104-109, ms.js:511-512, ms.js:517-517, ms.js:549-550, ms.js:568-568 ; k9_rows_v ms.js:418-425 ; k9_flat ms.js:455-456 — L 30, T 616, U 0, X 0
* `k9|rq_slide|` (entrée `k9RowsV`) : k9_rows_v ms.js:418-425 ; k9_flat ms.js:455-456 — L 10, T 267, U 0, X 0

## python

* `k1|natural|energy` (entrée `k1_natural`) : k1_natural ms.py:106-112, ms.py:115-119, ms.py:155-155 — L 13, T 208, U 0, X 0
* `k1|soa|energy` (entrée `k1_soa`) : k1_soa ms.py:127-130, ms.py:151-151 — L 4, T 86, U 0, X 0
* `k3|sw_packed|` (entrée `sub_run`) : k3 ms.py:186-187, ms.py:192-193, ms.py:195-207, ms.py:212-212, ms.py:215-215 ; sub_pool ms.py:43-51, ms.py:62-64 ; sub_run ms.py:54-59 — L 37, T 268, U 0, X 0
* `k3|sw_padded|` (entrée `sub_run`) : k3 ms.py:186-187, ms.py:192-193, ms.py:195-207, ms.py:212-212, ms.py:215-215 ; sub_pool ms.py:43-51, ms.py:62-64 ; sub_run ms.py:54-59 — L 37, T 268, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4_natural`) : k4_natural ms.py:219-224 — L 6, T 24, U 0, X 0
* `k4|tuned|` (entrée `k4_tuned`) : k4_tuned ms.py:235-235, ms.py:238-239 — L 3, T 35, U 0, X 0
* `k5|natural|` (entrée `k5_natural`) : k5_natural ms.py:275-279 — L 5, T 35, U 0, X 0
* `k5|tuned|` (entrée `sumprod`) : k5_tuned ms.py:284-284 — L 1, T 11, U 0, X 0
* `k6|mt_pool|q1` (entrée `SubPool`) : k6_sub ms.py:414-433, ms.py:439-443 ; k6_pool_close ms.py:461-461 ; sub_pool_cls ms.py:73-100 ; sub_pool ms.py:43-51, ms.py:62-64 ; q1_tuned ms.py:392-402 — L 74, T 840, U 0, X 0
* `k6|mt|q1` (entrée `sub_run`) : k6_sub ms.py:414-433, ms.py:439-443 ; k6_mt_close ms.py:459-459 ; sub_pool ms.py:43-51, ms.py:62-64 ; sub_run ms.py:54-59 ; q1_tuned ms.py:392-402 — L 55, T 677, U 0, X 0
* `k6|natural|q1` (entrée `q1_natural`) : q1_natural ms.py:378-389, ms.py:453-453 — L 13, T 170, U 0, X 0
* `k6|natural|q6` (entrée `q6_natural`) : q6_natural ms.py:298-304 — L 7, T 99, U 0, X 0
* `k6|rq_cols_mt|q6` (entrée `SubPool`) : k6_sub ms.py:414-433, ms.py:439-443 ; k6_pool_close ms.py:461-461 ; sub_pool_cls ms.py:73-100 ; sub_pool ms.py:43-51, ms.py:62-64 ; q6_columns ms.py:334-347 ; q6_tables ms.py:325-326, ms.py:329-331 — L 82, T 1057, U 0, X 0
* `k6|rq_cols|q6` (entrée `q6_columns`) : q6_columns ms.py:334-347 ; q6_tables ms.py:325-326, ms.py:329-331 — L 19, T 371, U 0, X 0
* `k6|tuned|q1` (entrée `q1_tuned`) : q1_tuned ms.py:392-402 ; q1_tuned_acc ms.py:450-450 — L 12, T 170, U 0, X 0
* `k7|natural|` (entrée `get`) : k7_natural ms.py:504-511 — L 8, T 53, U 0, X 0
* `k7|tuned_oa|` (entrée `k7_tuned_oa`) : k7_tuned_oa ms.py:469-486 — L 18, T 147, U 0, X 0
* `k8|natural|` (entrée `t_build`) : k8_natural ms.py:529-533, ms.py:540-550 — L 13, T 123, U 0, X 0
* `k8|tuned_val|` (entrée `a_build_val`) : k8_tuned_val ms.py:553-553, ms.py:569-570, ms.py:576-585 — L 13, T 137, U 0, X 0
* `k9|mt_pool|` (entrée `SubPool`) : k9_mt ms.py:700-700, ms.py:702-713, ms.py:720-723, ms.py:729-733, ms.py:741-744 ; sub_pool ms.py:43-51, ms.py:62-64 ; sub_pool_cls ms.py:73-100 — L 63, T 667, U 0, X 0
* `k9|mt|` (entrée `sub_run`) : k9_mt ms.py:700-700, ms.py:702-713, ms.py:720-723, ms.py:729-733, ms.py:741-744 ; sub_pool ms.py:43-51, ms.py:62-64 ; sub_run ms.py:54-59 — L 44, T 505, U 0, X 0
* `k9|natural|` (entrée `k9_natural`) : k9_natural ms.py:678-682 — L 5, T 99, U 0, X 0
* `k9|tuned|` (entrée `k9_rows`) : k9_rows ms.py:694-697 — L 4, T 120, U 0, X 0

## lua

* `k1|natural|energy` (entrée `k1_natural`) : k1_natural ms.lua:58-65, ms.lua:107-113 — L 15, T 237, U 0, X 0
* `k1|soa|energy` (entrée `k1_soa`) : k1_soa ms.lua:74-83, ms.lua:100-101 — L 12, T 203, U 0, X 0
* `k3|rmw_packed|` (entrée `stride`) : k3 ms.lua:144-146, ms.lua:150-153 — L 7, T 70, U 0, X 0
* `k3|rmw_padded|` (entrée `stride`) : k3 ms.lua:144-146, ms.lua:150-153 — L 7, T 70, U 0, X 0
* `k3|sw_packed|` (entrée `stride`) : k3 ms.lua:144-146, ms.lua:150-153 — L 7, T 70, U 0, X 0
* `k3|sw_padded|` (entrée `stride`) : k3 ms.lua:144-146, ms.lua:150-153 — L 7, T 70, U 0, X 0
* `k4|natural_unsorted|` (entrée `k4_natural`) : k4_natural ms.lua:163-170 — L 8, T 41, U 0, X 0
* `k4|swar|` (entrée `k4_swar`) : k4_swar ms.lua:204-223 — L 20, T 193, U 0, X 0
* `k4|tuned|` (entrée `k4_tuned`) : k4_tuned ms.lua:183-199 — L 17, T 135, U 0, X 0
* `k5|natural|` (entrée `k5_natural`) : k5_natural ms.lua:249-253 — L 5, T 37, U 0, X 0
* `k5|tuned|` (entrée `k5_tuned`) : k5_tuned ms.lua:254-260 — L 7, T 115, U 0, X 0
* `k6|mt|q1` (entrée `q1_tuned`) : k6_chunks_q1 ms.lua:384-384 ; q1_tuned ms.lua:350-363 — L 15, T 286, U 0, X 0
* `k6|natural|q1` (entrée `q1_natural`) : q1_natural ms.lua:338-349 — L 12, T 200, U 0, X 0
* `k6|natural|q6` (entrée `q6_natural`) : q6_natural ms.lua:274-281 — L 8, T 99, U 0, X 0
* `k6|rq_nest_mt|q6` (entrée `q6_nested`) : k6_nest_mt ms.lua:376-376 ; q6_nested ms.lua:297-308 — L 13, T 138, U 0, X 0
* `k6|rq_nest|q6` (entrée `q6_nested`) : q6_nested ms.lua:297-308 — L 12, T 100, U 0, X 0
* `k6|tuned|q1` (entrée `q1_tuned`) : k6_chunks_q1 ms.lua:384-384 ; q1_tuned ms.lua:350-363 — L 15, T 286, U 0, X 0
* `k7|natural|` (entrée `m`) : k7_natural ms.lua:425-430 — L 6, T 71, U 0, X 0
* `k7|rq_pack|` (entrée `ONE`) : k7_rq_pack ms.lua:445-451 — L 7, T 62, U 0, X 0
* `k8|natural|` (entrée `t_build`) : k8_natural ms.lua:473-479 — L 7, T 90, U 0, X 0
* `k8|tuned_val|` (entrée `a_build_val`) : k8_tuned_val ms.lua:480-480, ms.lua:488-488, ms.lua:492-499 — L 10, T 144, U 0, X 0
* `k9|natural|` (entrée `k9_natural`) : k9_natural ms.lua:564-569, ms.lua:593-593 — L 7, T 126, U 0, X 0
* `k9|rq_slide_mt|` (entrée `k9_flat_s`) : k9_flat_s ms.lua:579-589 — L 11, T 103, U 0, X 0

