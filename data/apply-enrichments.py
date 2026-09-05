"""Evidence-backed enrichment entrypoint; validates by default, writes only a new DB copy.

Legacy UI exports without field evidence must be re-reviewed and converted to
staged proposal format. See data/CONTRIBUTING-DATA.md. This no longer labels all
accepted proposals human_verified or modifies a source database on --dry-run.
"""
from stage_organizations import main

if __name__ == '__main__':
    main()
