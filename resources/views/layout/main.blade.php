<!DOCTYPE html>
<html lang="en">

<head>
    <!-- Required meta tags -->
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <title>Manufacture Dashboard</title>

    {{-- Import Tailwind CSS via Vite --}}
    @vite('resources/css/app.css')

    <!-- Favicon -->
    <link rel="icon" href="{{ asset('img/LogoWhite.svg') }}" />
</head>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Gothic+A1:wght@400;600;700&display=swap');

    :root {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
            Ubuntu, "Helvetica Neue", Helvetica, Arial, "PingFang SC",
            "Hiragino Sans GB", "Microsoft Yahei UI", "Microsoft Yahei",
            "Source Han Sans CN", sans-serif;
    }
</style>

<body class="h-auto w-screen bg-white">
    <!-- Flowbite CSS -->
    <link href="https://cdn.jsdelivr.net/npm/flowbite@2.5.1/dist/flowbite.min.css" rel="stylesheet" />

    <!-- Tempat Konten Halaman -->
    @yield('container')

    <!-- Flowbite JS -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.2.1/datepicker.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/flowbite@2.5.1/dist/flowbite.min.js"></script>
</body>

</html>
