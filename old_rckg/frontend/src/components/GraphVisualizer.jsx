import { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';

const GraphVisualizer = ({ elements }) => {
    const containerRef = useRef(null);
    const cyRef = useRef(null);

    useEffect(() => {
        if (!containerRef.current || !elements) return;

        // Log data for debugging
        console.log("GraphVisualizer received elements:", elements);

        // Removed early return for no elements
        // if (!elements.nodes || (elements.nodes.length === 0 && elements.edges.length === 0)) {
        //     console.warn("GraphVisualizer: No elements to render");
        //     return;
        // }

        // Destroy existing instance if any (cleanup)
        if (cyRef.current) {
            cyRef.current.destroy();
            cyRef.current = null;
        }

        // Initialize even if empty to show the grid/canvas
        cyRef.current = cytoscape({
            container: containerRef.current,
            elements: elements || [], // Safety fallback

            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': '#6366f1',
                        'label': 'data(label)',
                        'color': '#fafafa',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-size': '12px',
                        'width': '60px',
                        'height': '60px',
                        'border-width': 2,
                        'border-color': 'rgba(255,255,255,0.1)',
                        'overlay-opacity': 0,
                        'text-outline-width': 2,
                        'text-outline-color': '#18181b'
                    }
                },
                {
                    selector: 'node[type="Framework"]',
                    style: {
                        'background-color': '#ec4899', // Pink
                        'width': '80px',
                        'height': '80px',
                        'font-size': '14px',
                        'font-weight': 'bold'
                    }
                },
                {
                    selector: 'node[type="Requirement"]',
                    style: {
                        'background-color': '#10b981', // Emerald
                        'width': '40px',
                        'height': '40px',
                        'label': '' // Hide label for small nodes to reduce clutter? Or show on hover
                    }
                },
                {
                    selector: 'node:selected',
                    style: {
                        'border-width': 4,
                        'border-color': '#fff',
                        'label': 'data(label)' // Force show label
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': '#3f3f46',
                        'target-arrow-color': '#3f3f46',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'opacity': 0.5
                    }
                },
                {
                    selector: 'edge:selected',
                    style: {
                        'line-color': '#fafafa',
                        'width': 3,
                        'opacity': 1
                    }
                }
            ],

            layout: {
                name: 'grid' // Starts simple, then cose runs
            },

            wheelSensitivity: 0.3,
        });

        // Run layout only if we have nodes
        if (elements && elements.nodes && elements.nodes.length > 0) {
            cyRef.current.layout({
                name: 'cose',
                animate: true,
                animationDuration: 1000,
                randomize: true,
                componentSpacing: 100,
                nodeRepulsion: 400000,
            }).run();
        }

        return () => {
            if (cyRef.current) {
                cyRef.current.destroy();
                cyRef.current = null;
            }
        };
    }, []); // Re-run if elements *object* changes identity? Ideally pass prop dep

    // Update elements if they change
    useEffect(() => {
        if (cyRef.current && elements) {
            cyRef.current.json({ elements });
            if (elements.nodes && elements.nodes.length > 0) {
                cyRef.current.layout({ name: 'cose', animate: true, randomize: false }).run();
            }
        }
    }, [elements]);

    return (
        <div
            ref={containerRef}
            style={{
                width: '100%',
                height: '100%',
                background: 'var(--bg-app)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--glass-border)'
            }}
        />
    );
};

export default GraphVisualizer;
