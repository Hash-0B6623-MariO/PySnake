    class FollowerNode(Tile):
        def __init__(self, position, color):
            self.back = None
            self.front = None
            super().__init__(personality=8, position=position, color=color)

        def move(self, new_position):
            old_pos = self.position
            self.position = new_position
            if self.back:
                self.back.move(old_pos)

        def draw(self, surface:pygame.Surface, scale=1):
            super().draw(surface)
            if self.back:
                self.back.draw(surface)


    # Note: Only useful when implenting a character that can go back and forth from moving from the tail or head
    class Snake:
        # Planning on making this not exclusive to the character
        def __init__(self, position=(0, 0), direction=(1, 0)):
            self.head = Entity.FollowerNode(*position)
            self.tail = self.head
            self.vacated_pos = (0,0)
            self.grow_count = 0
            self.reaper = self._tail_generator()
            self.direction = direction

        def _tail_generator(self):
            while True:
                if self.grow_count > 0:
                    self.grow_count -= 1
                    self.tail.back = Entity.FollowerNode(*self.vacated_pos)
                    yield True
                else:
                    yield False

        def grow(self, amount=1):
            self.grow_count += amount

        def update(self):
            new_x, new_y = self.head.position[0] + self.direction[0], self.head.position[1] + self.direction[1]
            self.vacated_pos = self.tail.position
            self.head.move((new_x, new_y))

            if next(self.reaper):
                new_segment = Entity.FollowerNode()
                self.tail.back = new_segment
                self.tail = new_segment

        def draw(self, surface:pygame.Surface, scale=1):
            self.head.draw(surface, scale)

# Entity Instances
class Snake(Entity):
    _attributes = {
        "color": (0, 200, 0),
        "personality": 9
    }

    @classmethod
    def _node_factory_gen(cls):
        """Generator that accepts parent and position context for each new node."""
        context = yield None 
        while True:
            parent, pos = context
            node = Entity.FollowerNode(cls._attributes["personality"], cls._attributes["color"], parent, pos)
            context = yield node

    def __init__(self, position=(0, 0), direction=(1, 0), controller=None):
        super().__init__(
            personality=self._attributes["personality"],
            position=position,
            color=self._attributes["color"],
            controller=controller
        )
        
        self.node_factory = self._node_factory_gen()
        next(self.node_factory) # Prime the generator
        
        self.direction = direction
        self.last_moved_direction = direction
        
        # Initialize Persistent Tail with parent (self) and position
        self.tail = self.node_factory.send((self, position))
        self.back = self.tail 

    def grow(self):
        """O(1) Insertion: Wedges a node between head and the previous back."""
        # Use the head as the parent and its current position as the start
        new_segment = self.node_factory.send((self, self.position))
        
        old_back = self.back 
        
        # Re-link Head -> New Segment
        self.back = new_segment
        # (New segment's .front is already set to 'self' by the factory)
        
        # Re-link New Segment -> Old Back (the previous body or tail)
        new_segment.back = old_back
        if old_back:
            old_back.front = new_segment

    def move(self, new_position=None):
        old_self_pos = self.position
        if new_position is None:
            new_position = (self.position[0] + self.direction[0], 
                            self.position[1] + self.direction[1])

        if self.back:
            self.back.move(old_self_pos)

        self.last_moved_direction = self.direction
        super().move(new_position)

    def draw(self, surface, scale):
        super().draw(surface, scale)
        if self.back:
            self.back.draw(surface, scale)


