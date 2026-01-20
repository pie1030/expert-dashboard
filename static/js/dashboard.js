/**
 * 专家画像 Dashboard - 前端逻辑
 * 
 * 功能：
 * 1. 文件上传处理
 * 2. API 调用
 * 3. 图表渲染
 */

// ========================================
// 配色方案
// ========================================
const COLORS = {
    forestGreen: '#54A072',
    forestGreenLight: '#6BB38A',
    forestGreenDark: '#3D7A54',
    deepSeaBlue: '#6684A3',
    deepSeaBlueLight: '#7E99B4',
    greenPalette: ['#54A072', '#6BB38A', '#82C6A2', '#99D9BA', '#B0E6CD'],
    bluePalette: ['#6684A3', '#7E99B4', '#96AEC5', '#AEC3D6', '#C6D8E7'],
    mixed: ['#54A072', '#6684A3', '#6BB38A', '#7E99B4', '#82C6A2', '#96AEC5'],
    textDark: '#2C3E50',
    textGray: '#7F8C8D',
    bgColor: '#F7F8FA'
};

// ========================================
// 全局状态
// ========================================
let currentSessionId = null;
let charts = {};

// ========================================
// DOM 元素
// ========================================
const elements = {
    uploadSection: document.getElementById('upload-section'),
    dashboardSection: document.getElementById('dashboard-section'),
    uploadZone: document.getElementById('upload-zone'),
    fileInput: document.getElementById('file-input'),
    uploadBtn: document.getElementById('upload-btn'),
    uploadStatus: document.getElementById('upload-status'),
    resetBtn: document.getElementById('reset-btn'),
    expertCount: document.getElementById('expert-count')
};

// ========================================
// 初始化
// ========================================
function init() {
    setupEventListeners();
}

function setupEventListeners() {
    // 点击上传区域
    elements.uploadZone.addEventListener('click', () => {
        elements.fileInput.click();
    });
    
    // 文件选择
    elements.fileInput.addEventListener('change', handleFileSelect);
    
    // 拖拽上传
    elements.uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.uploadZone.classList.add('dragover');
    });
    
    elements.uploadZone.addEventListener('dragleave', () => {
        elements.uploadZone.classList.remove('dragover');
    });
    
    elements.uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.uploadZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
    
    // 上传按钮
    elements.uploadBtn.addEventListener('click', () => {
        elements.fileInput.click();
    });
    
    // 重置按钮
    elements.resetBtn.addEventListener('click', resetDashboard);
    
    // 窗口大小变化时重绘图表
    window.addEventListener('resize', () => {
        Object.values(charts).forEach(chart => {
            if (chart) chart.resize();
        });
    });
}

// ========================================
// 文件处理
// ========================================
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

async function handleFile(file) {
    // 验证文件
    if (!file.name.endsWith('.txt')) {
        showStatus('请上传 .txt 文件', 'error');
        return;
    }
    
    showStatus('正在上传...', '');
    elements.uploadBtn.disabled = true;
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || '上传失败');
        }
        
        if (result.success) {
            currentSessionId = result.session_id;
            showStatus(`成功解析 ${result.talent_count} 位专家`, 'success');
            
            // 加载 Dashboard
            await loadDashboard();
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        showStatus(`上传失败: ${error.message}`, 'error');
    } finally {
        elements.uploadBtn.disabled = false;
    }
}

function showStatus(message, type) {
    elements.uploadStatus.textContent = message;
    elements.uploadStatus.className = 'upload-status';
    if (type) {
        elements.uploadStatus.classList.add(type);
    }
}

// ========================================
// Dashboard 加载
// ========================================
async function loadDashboard() {
    try {
        const response = await fetch(`/api/dashboard/${currentSessionId}`);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || '获取数据失败');
        }
        
        if (result.success && result.stats) {
            // 切换到 Dashboard 视图
            elements.uploadSection.classList.add('hidden');
            elements.dashboardSection.classList.add('visible');
            
            // 渲染数据
            renderDashboard(result.stats);
        }
    } catch (error) {
        showStatus(`加载失败: ${error.message}`, 'error');
    }
}

function resetDashboard() {
    currentSessionId = null;
    elements.uploadSection.classList.remove('hidden');
    elements.dashboardSection.classList.remove('visible');
    elements.fileInput.value = '';
    showStatus('', '');
    
    // 销毁图表
    Object.values(charts).forEach(chart => {
        if (chart) chart.dispose();
    });
    charts = {};
}

// ========================================
// Dashboard 渲染
// ========================================
function renderDashboard(stats) {
    // 更新 KPI 卡片
    updateKPICards(stats);
    
    // 渲染图表
    renderSchoolTierChart(stats.school_tier_distribution);
    renderDegreeChart(stats.degree_distribution);
    renderTechStackChart(stats.tech_stack_distribution);
    renderTaskTypeChart(stats.task_type_distribution);
}

function updateKPICards(stats) {
    // 专家总数
    document.getElementById('kpi-total').textContent = stats.total_experts;
    
    // 高学历占比
    document.getElementById('kpi-masters-pct').textContent = stats.kpi.masters_and_above_pct + '%';
    document.getElementById('kpi-masters-count').textContent = stats.kpi.masters_and_above_count;
    
    // 名校背景
    document.getElementById('kpi-elite-pct').textContent = stats.kpi.elite_school_pct + '%';
    document.getElementById('kpi-elite-count').textContent = stats.kpi.elite_school_count;
    
    // 大厂经历
    document.getElementById('kpi-bigco-pct').textContent = stats.kpi.big_company_pct + '%';
    document.getElementById('kpi-bigco-count').textContent = stats.kpi.big_company_count;
    
    // 更新头部专家数量
    elements.expertCount.textContent = stats.total_experts;
}

// ========================================
// 图表渲染函数
// ========================================

// 通用 Tooltip 配置
const commonTooltip = {
    backgroundColor: 'rgba(255,255,255,0.98)',
    borderColor: '#e5e6e8',
    borderWidth: 1,
    padding: [12, 16],
    textStyle: {
        color: COLORS.textDark,
        fontSize: 13,
        fontFamily: 'Alegreya Sans, sans-serif'
    },
    extraCssText: 'box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-radius: 6px;'
};

// 通用字体配置
const commonFont = {
    fontFamily: 'Alegreya Sans, sans-serif'
};

// 学校层级分布
function renderSchoolTierChart(data) {
    const chartDom = document.getElementById('chart-school-tier');
    charts.schoolTier = echarts.init(chartDom);
    
    const chartData = Object.entries(data).map(([name, value]) => ({ name, value }));
    
    charts.schoolTier.setOption({
        tooltip: {
            ...commonTooltip,
            trigger: 'item',
            formatter: '{b}<br/>{c} 人 ({d}%)'
        },
        legend: {
            orient: 'vertical',
            right: '5%',
            top: 'center',
            itemWidth: 12,
            itemHeight: 12,
            itemGap: 14,
            textStyle: { fontSize: 13, color: COLORS.textDark, ...commonFont }
        },
        series: [{
            type: 'pie',
            radius: ['45%', '72%'],
            center: ['35%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 4,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: {
                show: true,
                position: 'inside',
                formatter: '{d}%',
                fontSize: 12,
                fontWeight: 600,
                color: '#fff',
                ...commonFont
            },
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 0, 0, 0.15)'
                }
            },
            data: chartData,
            color: COLORS.greenPalette
        }]
    });
}

// 学历分布
function renderDegreeChart(data) {
    const chartDom = document.getElementById('chart-degree');
    charts.degree = echarts.init(chartDom);
    
    const chartData = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .map(([name, value]) => ({ name, value }));
    
    charts.degree.setOption({
        tooltip: {
            ...commonTooltip,
            trigger: 'item',
            formatter: '{b}<br/>{c} 人 ({d}%)'
        },
        legend: {
            orient: 'vertical',
            right: '5%',
            top: 'center',
            itemWidth: 12,
            itemHeight: 12,
            itemGap: 14,
            textStyle: { fontSize: 13, color: COLORS.textDark, ...commonFont }
        },
        series: [{
            type: 'pie',
            radius: ['45%', '72%'],
            center: ['35%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 4,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: {
                show: true,
                position: 'inside',
                formatter: '{d}%',
                fontSize: 12,
                fontWeight: 600,
                color: '#fff',
                ...commonFont
            },
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 0, 0, 0.15)'
                }
            },
            data: chartData,
            color: COLORS.bluePalette
        }]
    });
}

// 技术栈分布
function renderTechStackChart(data) {
    const chartDom = document.getElementById('chart-tech-stack');
    charts.techStack = echarts.init(chartDom);
    
    const sortedData = Object.entries(data).sort((a, b) => a[1] - b[1]);
    const categories = sortedData.map(d => d[0]);
    const values = sortedData.map(d => d[1]);
    
    charts.techStack.setOption({
        tooltip: {
            ...commonTooltip,
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            formatter: function(params) {
                return params[0].name + '<br/>掌握人数: <strong>' + params[0].value + '</strong> 人';
            }
        },
        grid: {
            left: '3%',
            right: '14%',
            bottom: '5%',
            top: '5%',
            containLabel: true
        },
        xAxis: {
            type: 'value',
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { lineStyle: { color: COLORS.bgColor, type: 'dashed' } },
            axisLabel: { color: COLORS.textGray, fontSize: 11, ...commonFont }
        },
        yAxis: {
            type: 'category',
            data: categories,
            axisLine: { show: false },
            axisTick: { show: false },
            axisLabel: { color: COLORS.textDark, fontSize: 12, fontWeight: 500, ...commonFont }
        },
        series: [{
            type: 'bar',
            data: values,
            barWidth: 16,
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                    { offset: 0, color: COLORS.deepSeaBlue },
                    { offset: 1, color: COLORS.forestGreen }
                ]),
                borderRadius: [0, 6, 6, 0]
            },
            label: {
                show: true,
                position: 'right',
                formatter: '{c} 人',
                fontSize: 11,
                color: COLORS.textGray,
                ...commonFont
            }
        }]
    });
}

// 任务类型分布
function renderTaskTypeChart(data) {
    const chartDom = document.getElementById('chart-task-type');
    charts.taskType = echarts.init(chartDom);
    
    const chartData = Object.entries(data).map(([name, value]) => ({ name, value }));
    
    if (chartData.length === 0) {
        chartDom.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#7F8C8D;font-style:italic;">暂无任务类型数据</div>';
        return;
    }
    
    charts.taskType.setOption({
        tooltip: {
            ...commonTooltip,
            trigger: 'item',
            formatter: '{b}<br/>{c} 次 ({d}%)'
        },
        legend: {
            orient: 'vertical',
            right: '5%',
            top: 'center',
            itemWidth: 12,
            itemHeight: 12,
            textStyle: { fontSize: 12, color: COLORS.textDark, ...commonFont }
        },
        series: [{
            type: 'pie',
            radius: ['30%', '72%'],
            center: ['35%', '50%'],
            roseType: 'radius',
            itemStyle: {
                borderRadius: 4,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: {
                show: false
            },
            emphasis: {
                label: { show: true, fontSize: 12, fontWeight: 600, ...commonFont }
            },
            data: chartData,
            color: COLORS.mixed
        }]
    });
}

// ========================================
// 启动
// ========================================
document.addEventListener('DOMContentLoaded', init);
