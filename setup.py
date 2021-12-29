#!/usr/bin/env python3
from setuptools import setup

# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = 'skill-lovecraft-comics.jarbasai=skill_lovecraft_comics:LovecraftComicsSkill'

setup(
    # this is the package name that goes on pip
    name='ovos-skill-lovecraft-comics',
    version='0.0.1',
    description='ovos lovecraft comics skill plugin',
    url='https://github.com/JarbasSkills/skill-lovecraft-comics',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    package_dir={"skill_lovecraft_comics": ""},
    package_data={'skill_lovecraft_comics': ['locale/*', 'res/*', 'ui/*']},
    packages=['skill_lovecraft_comics'],
    include_package_data=True,
    install_requires=["ovos_workshop~=0.0.5a1"],
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
