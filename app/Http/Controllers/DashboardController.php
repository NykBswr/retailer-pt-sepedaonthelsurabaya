<?php

namespace App\Http\Controllers;

use App\Models\User;
use App\Models\Dashboard;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Auth;
use App\Models\FactJumlahPerusahaanProvinsi;

class DashboardController extends Controller
{
    public function getJumlahPerusahaanBySektorWaktu()
    {
        $data = DB::table('fact_jumlah_perusahaan_kbli')
            ->join('dim_waktu', 'fact_jumlah_perusahaan_kbli.ID_Waktu', '=', 'dim_waktu.ID_Waktu')
            ->join('dim_sektor_industri', 'fact_jumlah_perusahaan_kbli.KBLI', '=', 'dim_sektor_industri.KBLI')
            ->select('dim_waktu.Tahun', 'dim_sektor_industri.Nama_Sektor', DB::raw('SUM(fact_jumlah_perusahaan_kbli.Jumlah_Perusahaan_Industri) as total_perusahaan'))
            ->groupBy('dim_waktu.Tahun', 'dim_sektor_industri.Nama_Sektor')
            ->orderBy('dim_waktu.Tahun', 'asc')
            ->orderBy('total_perusahaan', 'desc')
            ->get();

        $formattedData = [];
        $categories = [];

        // Ambil top 5 sektor untuk setiap tahun
        foreach ($data->groupBy('Tahun') as $tahun => $sektors) {
            $top5Sektors = $sektors->sortByDesc('total_perusahaan')->take(4);

            foreach ($top5Sektors as $row) {
                $formattedData[$row->Nama_Sektor][$row->Tahun] = $row->total_perusahaan;
            }

            if (!in_array($tahun, $categories)) {
                $categories[] = $tahun;
            }
        }

        return [
            'formattedData' => $formattedData,
            'categories' => $categories
        ];
    }

    public function getNilaiTambahBySektorSkala()
    {
        $data = DB::table('fact_nilai_tambah')
            ->join('dim_skala_industri', 'fact_nilai_tambah.Skala_ID', '=', 'dim_skala_industri.Skala_ID')
            ->join('dim_sektor_industri', 'fact_nilai_tambah.Sektor_ID', '=', 'dim_sektor_industri.Sektor_ID') // Ganti dengan kolom yang benar
            ->select('dim_skala_industri.Jenis_Skala', 'dim_sektor_industri.Nama_Sektor', 
            DB::raw('SUM(fact_nilai_tambah.Nilai_Tambah_Industri) as total_nilai_tambah'))
            ->groupBy('dim_skala_industri.Jenis_Skala', 'dim_sektor_industri.Nama_Sektor')
            ->orderBy('dim_skala_industri.Jenis_Skala', 'asc')
            ->orderBy('total_nilai_tambah', 'desc') 
            ->get();

        $formattedData = [];
        $categories = [];

        // Ambil top 5 sektor untuk setiap tahun
        foreach ($data->groupBy('Jenis_Skala') as $Skala_ID => $sektors) {
            $top5Sektors = $sektors->sortByDesc('total_nilai_tambah')->take(5);

            foreach ($top5Sektors as $row) {
                $formattedData[$row->Nama_Sektor][$row->Jenis_Skala] = $row->total_nilai_tambah; // Sesuaikan dengan nilai tambah
            }

            if (!in_array($Skala_ID, $categories)) {
                $categories[] = $Skala_ID;
            }
        }

        return [
            'formattedData' => $formattedData,
            'categories' => $categories
        ];
    }

    public function getJumlahPerusahaanBySkalaIndustri()
    {
        $data = DB::table('fact_jumlah_perusahaan_kbli')
            ->join('dim_skala_industri', 'fact_jumlah_perusahaan_kbli.Skala_ID', '=', 'dim_skala_industri.Skala_ID')
            ->select('dim_skala_industri.Jenis_Skala', DB::raw('COUNT(fact_jumlah_perusahaan_kbli.KBLI) as Jumlah_Perusahaan_Industri'))
            ->groupBy('dim_skala_industri.Jenis_Skala')
            ->get();

        $seriesData = [];
        $labels = [];

        foreach ($data as $row) {
            $seriesData[] = $row->Jumlah_Perusahaan_Industri;
            $labels[] = $row->Jenis_Skala;
        }

        return [
            'seriesData' => $seriesData,
            'labels' => $labels
        ];
    }

    public function getPertumbuhanProduksiByProvinsi()
    {
        $data = DB::table('fact_pertumbuhan_produksi')
            ->join('dim_provinsi', 'fact_pertumbuhan_produksi.Provinsi_ID', '=', 'dim_provinsi.Provinsi_ID')
            ->join('dim_waktu', 'fact_pertumbuhan_produksi.ID_Waktu', '=', 'dim_waktu.ID_Waktu')
            ->select('dim_provinsi.Provinsi', 'dim_waktu.Tahun', 
                    DB::raw('SUM(fact_pertumbuhan_produksi.Nilai_Tambah_Industri) as total_pertumbuhan'))
            ->whereIn('dim_provinsi.Provinsi', ['BALI', 'DKI JAKARTA', 'JAWA TIMUR'])
            ->groupBy('dim_provinsi.Provinsi', 'dim_waktu.Tahun')
            ->orderBy('dim_waktu.Tahun', 'asc')
            ->get();

        $seriesData = [];
        $categories = [];

        $groupedData = $data->groupBy('Provinsi');

        foreach ($groupedData as $provinsi => $years) {
            $dataSeries = [];
            foreach ($years as $year) {
                $dataSeries[] = $year->total_pertumbuhan;
                if (!in_array($year->Tahun, $categories)) {
                    $categories[] = $year->Tahun;
                }
            }
            $seriesData[] = [
                'name' => $provinsi,
                'data' => $dataSeries
            ];
        }

        return [
            'seriesData' => $seriesData,
            'categories' => $categories
        ];
    }

    public function getPerbandinganNilaiOutputBySkala()
    {
        $data = DB::table('fact_nilai_output')
            ->join('dim_skala_industri', 'fact_nilai_output.Skala_ID', '=', 'dim_skala_industri.Skala_ID')
            ->select('dim_skala_industri.Jenis_Skala', 
                    DB::raw('SUM(fact_nilai_output.Nilai_Output_Industri) as total_nilai_output'))
            ->groupBy('dim_skala_industri.Jenis_Skala')
            ->get();

        $categories = ['Mikro', 'Kecil'];
        $outputMikro = 0;
        $outputKecil = 0;

        foreach ($data as $row) {
            if ($row->Jenis_Skala == 'Mikro') {
                $outputMikro += $row->total_nilai_output;
            } elseif ($row->Jenis_Skala == 'Kecil') {
                $outputKecil += $row->total_nilai_output;
            }
        }

        $seriesData = [
            [
                'name' => 'Total Nilai Output',
                'data' => [$outputMikro, $outputKecil]
            ]
        ];

        // Kirim data ke view
        return [
            'outputMikro' => $outputMikro,
            'outputKecil' => $outputKecil
        ];
    }

    public function getTop5NilaiOutputBySektor()
    {
        // Ambil data dari tabel nilai output dan sektor industri
        $data = DB::table('fact_nilai_output')
            ->join('dim_sektor_industri', 'fact_nilai_output.Sektor_ID', '=', 'dim_sektor_industri.Sektor_ID')
            ->select('dim_sektor_industri.Nama_Sektor', 
                    DB::raw('SUM(fact_nilai_output.Nilai_Output_Industri) as total_nilai_output'))
            ->groupBy('dim_sektor_industri.Nama_Sektor')
            ->orderByDesc('total_nilai_output')
            ->take(5) 
            ->get();

        $categories = [];
        $outputValues = [];

        foreach ($data as $row) {
            $categories[] = $row->Nama_Sektor; 
            $outputValues[] = $row->total_nilai_output;
        }

        // Kirim data ke view
        return [
            'categories' => $categories,
            'outputValues' => $outputValues
        ];
    }

    public function getTotalPerusahaanIndustriKecilMikro()
    {
        // Ambil data untuk tahun 2022 dan 2023
        $data2021 = DB::table('fact_jumlah_perusahaan_provinsi')
            ->join('dim_skala_industri', 'fact_jumlah_perusahaan_provinsi.Skala_ID', '=', 'dim_skala_industri.Skala_ID')
            ->join('dim_waktu', 'fact_jumlah_perusahaan_provinsi.ID_Waktu', '=', 'dim_waktu.ID_Waktu')
            ->whereIn('dim_skala_industri.Jenis_Skala', ['Kecil', 'Mikro'])
            ->where('dim_waktu.Tahun', 2021) 
            ->sum('fact_jumlah_perusahaan_provinsi.Jumlah_Perusahaan_Industri');

        $data2022 = DB::table('fact_jumlah_perusahaan_provinsi')
            ->join('dim_skala_industri', 'fact_jumlah_perusahaan_provinsi.Skala_ID', '=', 'dim_skala_industri.Skala_ID')
            ->join('dim_waktu', 'fact_jumlah_perusahaan_provinsi.ID_Waktu', '=', 'dim_waktu.ID_Waktu')
            ->whereIn('dim_skala_industri.Jenis_Skala', ['Kecil', 'Mikro'])
            ->where('dim_waktu.Tahun', 2022)
            ->sum('fact_jumlah_perusahaan_provinsi.Jumlah_Perusahaan_Industri');

        // Hitung persentase kenaikan atau penurunan
        if ($data2021 > 0) {
            $persentasePerubahan = (($data2022 - $data2021) / $data2021) * 100;
        } else {
            $persentasePerubahan = 0;
        }

        return [
            'total2021' => $data2021,
            'total2022' => $data2022,
            'persentasePerubahan' => $persentasePerubahan
        ];
    }

    public function index(Request $request)
    {
        $user = Auth::user();

        if (!$user) {
            return redirect('/');
        }

        $jumlahPerusahaan = $this->getJumlahPerusahaanBySektorWaktu();
        $NilaiTambah = $this->getNilaiTambahBySektorSkala();
        $JumlahPerusahaanBySkalaIndustri = $this->getJumlahPerusahaanBySkalaIndustri();
        $PertumbuhanProduksiByProvinsi = $this-> getPertumbuhanProduksiByProvinsi();
        $PerbandinganNilaiOutputBySkala = $this-> getPerbandinganNilaiOutputBySkala();
        $NilaiOutputBySektor = $this-> getTop5NilaiOutputBySektor();
        $TotalPerusahaanIndustriKecilMikro = $this-> getTotalPerusahaanIndustriKecilMikro();
        // dd($PerbandinganNilaiOutputBySkala);

        return view('dashboard.main', [
            'user' => $user,
            'formattedData' => $jumlahPerusahaan['formattedData'],
            'categories' => $jumlahPerusahaan['categories'],
            'formattedData2' => $NilaiTambah['formattedData'],
            'categories2' => $NilaiTambah['categories'],
            'seriesData' => $JumlahPerusahaanBySkalaIndustri['seriesData'],
            'labels' => $JumlahPerusahaanBySkalaIndustri['labels'],
            'seriesData2' => $PertumbuhanProduksiByProvinsi['seriesData'],
            'categories3' => $PertumbuhanProduksiByProvinsi['categories'],
            'outputMikro' => $PerbandinganNilaiOutputBySkala['outputMikro'],
            'outputKecil' => $PerbandinganNilaiOutputBySkala['outputKecil'],
            'categories5' => $NilaiOutputBySektor['categories'],
            'outputValues' => $NilaiOutputBySektor['outputValues'],
            'total2022' => $TotalPerusahaanIndustriKecilMikro['total2022'],
            'persentasePerubahan' => $TotalPerusahaanIndustriKecilMikro['persentasePerubahan'],
        ]);
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Display the specified resource.
     */
    public function show(Dashboard $dashboard)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(Dashboard $dashboard)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, Dashboard $dashboard)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Dashboard $dashboard)
    {
        //
    }
}
