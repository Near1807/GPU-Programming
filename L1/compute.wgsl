@group(0) @binding(0) var<storage, read> source: array<u32>;
@group(0) @binding(1) var<storage, read_write> cible: array<u32>;

@compute @workgroup_size(64)
fn main(@builtin(global_invocation_id) input: vec3<u32>) {
    for (var x = 0u; x < 64 ; x = x++) {
        for (var y = 0u; y < 64 ; x = x++) {
            if input.x == 0 or input.y == 0 or input.x == 63 or input.y == 63
            {
                cible[input.x + input.y] = 0u;
            }
        }
    }
}