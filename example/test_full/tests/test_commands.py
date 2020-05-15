from .base import GenericModelTestBase
from computedfields.models import ComputedFieldsModelType
from computedfields.graph import CycleNodeException
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO
import pickle
from django.conf import settings
import os


class CommandTests(GenericModelTestBase):
    """
    Tests the management commands.
    """
    def setUp(self):
        self.setDeps({
            # deps only to itself
            'B': {'func': lambda self: self.name},
            # one fk step deps to comp field
            'C': {'depends': ['f_cb#comp'],
                  'func': lambda self: self.name + self.f_cb.comp},
            'D': {'depends': ['f_dc#comp'],
                  'func': lambda self: self.name + self.f_dc.comp},
            # multi fk steps deps to non comp field
            'E': {'depends': ['f_ed.f_dc.f_cb.f_ba#name'],
                  'func': lambda self: self.name + self.f_ed.f_dc.f_cb.f_ba.name},
            # multi fk steps deps to comp field
            'F': {'depends': ['f_fe.f_ed.f_dc.f_cb#name'],
                  'func': lambda self: self.name + self.f_fe.f_ed.f_dc.f_cb.name}
        })

    def tearDown(self):
        self.resetDeps()

    def test_rendergraph(self):
        # TODO: test for output
        self.assertEqual(self.graph.is_cyclefree, True)
        call_command('rendergraph', 'output', verbosity=0)
        os.remove('output.pdf')

    def test_rendergraph_with_cycle(self):
        import sys

        # raises due to get_nodepaths() in _resolve_dependencies()
        self.assertRaises(
            CycleNodeException,
            lambda: self.setDeps({
                    'A': {'depends': ['f_ag#comp']},
                    'G': {'depends': ['f_ga#comp']},
                })
        )
        self.assertEqual(ComputedFieldsModelType._graph.is_cyclefree, False)
        stdout = sys.stdout
        sys.stdout = StringIO()
        call_command('rendergraph', 'output', verbosity=0)
        # should have printed cycle info on stdout
        self.assertIn('Warning -  1 cycles in dependencies found:', sys.stdout.getvalue())
        sys.stdout = stdout

    def test_updatedata(self):
        # TODO: advanced test case
        self.models.A(name='a').save()
        call_command('updatedata', verbosity=0)

    def test_createmap(self):
        # save old value
        old_map = None
        map_set = hasattr(settings, 'COMPUTEDFIELDS_MAP')
        if map_set:
            old_map = settings.COMPUTEDFIELDS_MAP

        # should not fail
        settings.COMPUTEDFIELDS_MAP = os.path.join(settings.BASE_DIR, 'map.test')
        call_command('createmap', verbosity=0)
        with open(os.path.join(settings.BASE_DIR, 'map.test'), 'rb') as f:
            pickled_data = pickle.load(f)
            map = pickled_data['lookup_map']
            fk_map = pickled_data['fk_map']
            local_mro = pickled_data['local_mro']
            self.assertDictEqual(map, ComputedFieldsModelType._map)
            self.assertDictEqual(fk_map, ComputedFieldsModelType._fk_map)
            self.assertDictEqual(local_mro, ComputedFieldsModelType._local_mro)
        os.remove(os.path.join(settings.BASE_DIR, 'map.test'))

        # restore old  value
        if map_set:
            settings.COMPUTEDFIELDS_MAP = old_map

    def test_createmap_without_setting(self):
        # save old value
        old_map = None
        map_set = hasattr(settings, 'COMPUTEDFIELDS_MAP')
        if map_set:
            old_map = settings.COMPUTEDFIELDS_MAP

        # this should fail
        delattr(settings, 'COMPUTEDFIELDS_MAP')
        self.assertRaisesMessage(CommandError, 'COMPUTEDFIELDS_MAP is not set in settings.py, abort.',
            lambda : call_command('createmap', verbosity=0))

        # restore old  value
        if map_set:
            settings.COMPUTEDFIELDS_MAP = old_map
