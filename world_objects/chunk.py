from settings import *
from terrain_gen import *
from meshes.chunk_mesh import ChunkMesh


class Chunk:
    def __init__(self, world, position):
        self.app = world.app
        self.world = world
        self.position = position
        self.m_model = self.get_model_matrix()
        self.voxels = None
        self.mesh: ChunkMesh = None
        self.is_empty = True

        self.center = (glm.vec3(self.position) + 0.5) * CHUNK_SIZE
        self.is_on_frustum = self.app.player.frustum.is_on_frustum

    def build_mesh(self):
        self.mesh = ChunkMesh(self)

    def build_voxels(self):
        # Empty Chunk
        voxels = np.zeros(CHUNK_VOL, dtype="uint8")

        # Fill Chunk
        cx, cy, cz = glm.ivec3(self.position) * CHUNK_SIZE
        self.generate_terrain(voxels, cx, cy, cz)

        if np.any(voxels):
            self.is_empty = False

        return voxels    

    def get_model_matrix(self):
        m_model = glm.translate(glm.mat4(), glm.vec3(self.position) * CHUNK_SIZE)
        return m_model

    def render(self):
        if not self.is_empty and self.is_on_frustum(self):
            self.set_uniform()
            self.mesh.render()

    def set_uniform(self):
        self.mesh.program["m_model"].write(self.m_model)

    @staticmethod
    @njit
    def generate_terrain(voxels, cx, cy, cz):
        for x in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                wx = x + cx
                wz = z + cz
                world_height = get_height(wx, wz)
                local_height = min(world_height - cy, CHUNK_SIZE)
                for y in range(local_height):
                    wy = y + cy
                    set_voxel_id(voxels, x, y, z, wx, wy, wz, world_height)