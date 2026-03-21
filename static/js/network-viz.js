/**
 * Helios Neural Field Visualization
 * â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
 * D3.js force-directed graph â€” undirected, no hierarchy.
 * Concentric influence rings. Pulsing energy propagation.
 * Gold on dark. No "above" or "below".
 */

function renderField(data) {
    const container = document.getElementById('network-viz');
    container.innerHTML = '';

    const width = container.clientWidth;
    const height = container.clientHeight;

    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const defs = svg.append('defs');

    // Radial gradient for concentric rings
    const ringGrad = defs.append('radialGradient')
        .attr('id', 'ringGrad')
        .attr('cx', '50%').attr('cy', '50%').attr('r', '50%');
    ringGrad.append('stop').attr('offset', '0%').attr('stop-color', '#f59e0b').attr('stop-opacity', 0.08);
    ringGrad.append('stop').attr('offset', '100%').attr('stop-color', '#f59e0b').attr('stop-opacity', 0);

    // Glow filter
    const glow = defs.append('filter').attr('id', 'nodeGlow');
    glow.append('feGaussianBlur').attr('stdDeviation', '4').attr('result', 'blur');
    const merge = glow.append('feMerge');
    merge.append('feMergeNode').attr('in', 'blur');
    merge.append('feMergeNode').attr('in', 'SourceGraphic');

    // Background concentric rings (influence visualization)
    const ringGroup = svg.append('g').attr('class', 'influence-rings');
    const cx = width / 2, cy = height / 2;
    for (let i = 5; i >= 1; i--) {
        ringGroup.append('circle')
            .attr('cx', cx).attr('cy', cy)
            .attr('r', i * Math.min(width, height) * 0.08)
            .attr('fill', 'none')
            .attr('stroke', '#f59e0b')
            .attr('stroke-opacity', 0.06)
            .attr('stroke-width', 1)
            .attr('stroke-dasharray', '4,8');
    }

    // Node state colors â€” no hierarchy, just connectivity
    const stateColor = {
        'stable': '#f59e0b',       // Gold â€” fully saturated
        'propagating': '#fbbf24',   // Light gold â€” active
        'connected': '#3b82f6',     // Blue â€” growing
        'acknowledged': '#8b5cf6',  // Purple â€” new
        'instantiated': '#6366f1'   // Indigo â€” just joined
    };

    // Size based on link count, not "rank"
    const sizeScale = d3.scaleLinear()
        .domain([0, 5])
        .range([6, 18]);

    // Build nodes for D3
    const nodes = data.nodes.map(n => ({
        id: n.id,
        name: n.name,
        hops: n.hops,
        node_state: n.node_state,
        link_count: n.link_count || 0,
        activity: n.activity,
        is_origin: n.is_origin,
        energy_weight: n.energy_weight || 1.0,
        radius: n.is_origin ? 24 : sizeScale(n.link_count || 1)
    }));

    const nodeIds = new Set(nodes.map(n => n.id));
    const links = data.edges
        .filter(e => nodeIds.has(e.source) && nodeIds.has(e.target))
        .map(e => ({
            source: e.source,
            target: e.target
        }));

    // Force simulation â€” undirected, no hierarchy bias
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-250))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(d => d.radius + 8))
        .force('x', d3.forceX(width / 2).strength(0.03))
        .force('y', d3.forceY(height / 2).strength(0.03));

    // Link lines
    const link = svg.append('g')
        .selectAll('line')
        .data(links)
        .enter().append('line')
        .attr('stroke', '#f59e0b')
        .attr('stroke-width', 1.5)
        .attr('stroke-opacity', 0.2);

    // Energy pulse animation on links
    const pulseGroup = svg.append('g');
    links.forEach((l, i) => {
        pulseGroup.append('circle')
            .attr('class', 'energy-pulse')
            .attr('r', 2)
            .attr('fill', '#f59e0b')
            .attr('opacity', 0)
            .datum(l);
    });

    // Node groups
    const node = svg.append('g')
        .selectAll('g')
        .data(nodes)
        .enter().append('g')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    // Node outer glow (for origin)
    node.filter(d => d.is_origin)
        .append('circle')
        .attr('r', d => d.radius + 8)
        .attr('fill', 'none')
        .attr('stroke', '#f59e0b')
        .attr('stroke-width', 2)
        .attr('stroke-opacity', 0.3)
        .attr('class', 'origin-ring');

    // Node circles
    node.append('circle')
        .attr('r', d => d.radius)
        .attr('fill', d => stateColor[d.node_state] || '#6366f1')
        .attr('stroke', d => d.is_origin ? '#64d2ff' : 'rgba(41,151,255,0.2)')
        .attr('stroke-width', d => d.is_origin ? 2.5 : 1)
        .attr('filter', d => d.is_origin ? 'url(#nodeGlow)' : null)
        .attr('cursor', 'pointer')
        .on('mouseover', function(event, d) {
            d3.select(this).attr('stroke', '#64d2ff').attr('stroke-width', 2.5);
            showDetail(d);
        })
        .on('mouseout', function(event, d) {
            if (!d.is_origin) {
                d3.select(this).attr('stroke', 'rgba(41,151,255,0.2)').attr('stroke-width', 1);
            }
        });

    // Link count indicator (small number)
    node.append('text')
        .text(d => d.is_origin ? '☀' : (d.link_count || ''))
        .attr('text-anchor', 'middle')
        .attr('dy', d => d.is_origin ? 5 : 4)
        .attr('fill', d => d.is_origin ? '#64d2ff' : 'rgba(255,255,255,0.7)')
        .attr('font-size', d => d.is_origin ? '14px' : '9px')
        .attr('font-family', 'Inter, sans-serif')
        .attr('font-weight', '600');

    // Node labels
    node.append('text')
        .text(d => d.name)
        .attr('text-anchor', 'middle')
        .attr('dy', d => d.radius + 16)
        .attr('fill', '#8888aa')
        .attr('font-size', '10px')
        .attr('font-family', 'Inter, sans-serif');

    // Tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Energy pulse animation
    function animatePulse() {
        pulseGroup.selectAll('.energy-pulse')
            .transition()
            .duration(2000)
            .delay((d, i) => i * 200)
            .attr('opacity', 0.6)
            .attrTween('cx', function(d) {
                return function(t) {
                    return d.source.x + (d.target.x - d.source.x) * t;
                };
            })
            .attrTween('cy', function(d) {
                return function(t) {
                    return d.source.y + (d.target.y - d.source.y) * t;
                };
            })
            .transition()
            .duration(100)
            .attr('opacity', 0)
            .on('end', function(d, i) {
                if (i === 0) setTimeout(animatePulse, 3000);
            });
    }
    setTimeout(animatePulse, 2000);

    // Drag
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x; d.fy = d.y;
    }
    function dragged(event, d) {
        d.fx = event.x; d.fy = event.y;
    }
    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null; d.fy = null;
    }

    function showDetail(d) {
        const detail = document.getElementById('node-detail');
        if (!detail) return;
        detail.style.display = 'block';
        document.getElementById('detail-name').textContent = `${d.name} (${d.id})`;
        document.getElementById('detail-state').textContent = d.node_state;
        document.getElementById('detail-links').textContent = `${d.link_count}/5 links`;
        document.getElementById('detail-hops').textContent = `${d.hops} hops from you`;
        document.getElementById('detail-energy').textContent = `${(d.energy_weight * 100).toFixed(3)}% energy weight`;
    }
}
