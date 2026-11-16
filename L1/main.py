from wgpu import *
import wgpu
import numpy as np
import random as rd
def create_initial_data(size:(int, int), starting_population:int):
    data0 = np.zeros(size, dtype=np.uint32)
    data1 = np.zeros(size, dtype=np.uint32)
    for i in range(starting_population):
        x = rd.randint(0, size[0]-1)
        y = rd.randint(0, size[1]-1)
        data0[x][y] = 1
    return data0,data1

def life_state_calculator(reader, writer):
    for x in range(reader.shape[0]):
        for y in range(reader.shape[1]):
            if x == 0 or y == 0 or x == reader.shape[0]-1 or y == reader.shape[1]-1:
                writer[x,y] = 0
            else: 
                live_neighbors = 0
                for i in range(x-1, x+2):
                    for j in range(y-1, y+2):
                        if reader[i,j] == 1 and (i != x or j != y):
                            live_neighbors += 1
                if reader[x,y] == 1:
                    if live_neighbors == 2 or live_neighbors == 3:
                        writer[x,y] = 1
                    else:
                        writer[x,y] = 0
                else:
                    if live_neighbors == 3:
                        writer[x,y] = 1
                    else:
                        writer[x,y] = 0
    return writer


data0, data1= create_initial_data((10, 10), 20)
print (data0)
print(life_state_calculator(data0, data1))

    
                        



#GPU setup
adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
device = adapter.request_device_sync()
#Buffer Creation
buffer0 = device.create_buffer_with_data(data=data0, usage=BufferUsage.STORAGE)

buffer1 = device.create_buffer_with_data(data=data1, usage=BufferUsage.STORAGE)
#bind group creation
bind_group_layout = device.create_bind_group_layout(
    entries=[
        {
            "binding": 0,
            "visibility": ShaderStage.COMPUTE,
            "buffer": {"type": BufferBindingType.read_only_storage},
        },
        {
            "binding": 1,
            "visibility": ShaderStage.COMPUTE,
            "buffer": {"type": BufferBindingType.storage},
        }
    ]
)
# Load the source code to execute on the GPU
shader_source = """
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
"""

shader_module = device.create_shader_module(code=shader_source)

# A Pipeline may use multiple Bind Group
pipeline_layout = device.create_pipeline_layout(
    bind_group_layouts=[bind_group_layout]
)

pipeline = device.create_compute_pipeline(
    layout=pipeline_layout,
    compute={
        "module": shader_module,
        "entry_point": "main",
    },
)

bind_group = device.create_bind_group(
    layout=bind_group_layout,
    entries=[
        {"binding": 0, "resource": {"buffer": buffer0, "offset": 0, "size": buffer0.size}},
        {"binding": 1, "resource": {"buffer": buffer1, "offset": 0, "size": buffer1.size}},
    ],
)