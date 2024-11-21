from test_maestro.conftest import BaseMaestroTest


class TestMaestroStr(BaseMaestroTest):
    def test_no_targets_set(self):
        assert str(self.maestro) == 'MaestroTestImpl(targets={0: None, 1: None, 2: None})'

    def test_targets_set(self):
        self.maestro.set_target(0, 42)
        self.maestro.set_target(1, 43)
        self.maestro.set_target(2, 44)

        assert str(self.maestro) == 'MaestroTestImpl(targets={0: 42, 1: 43, 2: 44})'
