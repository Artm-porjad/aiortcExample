from setuptools import setup, find_namespace_packages

settings = {
    'name': 'Webcam',
    'description': 'webcam',
    'zip_safe': False,
    'include_package_data': True,
    'packages': find_namespace_packages(),
}


def main():
    setup(**settings)


if __name__ == '__main__':
    main()
