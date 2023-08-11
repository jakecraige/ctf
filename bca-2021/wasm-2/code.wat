(module
  (type (;0;) (func (param i32 i32) (result i32)))
  (type (;1;) (func (param i32) (result i32)))
  (func $cmp (type 0) (param $v0 i32) (param $v1 i32) (result i32)
    (local $v2 i32)
    loop  ;; label = @1
      local.get $v2
      local.get $v0
      i32.add
      i32.load8_u
      local.get $v2
      local.get $v1
      i32.add
      i32.load8_u
      local.get $v2
      i32.const 9
      i32.mul
      i32.const 127
      i32.and
      i32.xor
      i32.ne
      local.get $v2
      i32.const 27
      i32.ne
      i32.and
      if  ;; label = @2
        i32.const 0
        return
      end
      local.get $v2
      i32.const 1
      i32.add
      local.tee $v2
      i32.const 1
      i32.sub
      local.get $v0
      i32.add
      i32.load8_u
      i32.eqz
      if  ;; label = @2
        i32.const 1
        return
      end
      br 0 (;@1;)
    end
    i32.const 0
    return)
  (func $checkFlag (type 1) (param $a i32) (result i32)
    local.get $a
    i32.const 1000
    call $cmp
    return)
  (memory (;0;) 1)
  (export "memory" (memory 0))
  (export "checkFlag" (func $checkFlag))
  (data (;0;) (i32.const 1000) "bjsxPKMH|\227N\1bD\043b]PR\19e%\7f/;\17"))
