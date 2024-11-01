import { type FunctionComponent, useEffect, useState } from "react";

export const Search: FunctionComponent = () => {
    const [widgetDocumentContent, setWidgetDocumentContent] = useState("");

    const retryFindingShadowRoot = (
        bodyNode: HTMLElement,
        retries: number,
        delay: number,
    ) => {
        const attempt = () => {
            const widgetShadowRoot = bodyNode.shadowRoot;
            if (widgetShadowRoot) {
                handleShadowRootWidgetDiv(widgetShadowRoot, bodyNode);
            } else if (retries > 0) {
                console.log("No shadow root found, retrying...");
                setTimeout(attempt, delay);
            } else {
                console.log("No shadow root found after retries.");
            }
        };
        attempt();
    };

    const handleShadowRootWidgetDiv = (
        widgetShadowRoot: ShadowRoot,
        bodyNode: HTMLElement,
    ) => {
        setTimeout(() => {
            const shadowRootWidgetDiv = widgetShadowRoot.querySelector("div");
            if (shadowRootWidgetDiv) {
                bodyNode.style.display = "block";
                shadowRootWidgetDiv.style.top = "unset";
            } else {
                console.log("No div element found in shadowRoot.");
            }
        }, 250);
    };

    const processAddedNodes = (addedNodes: NodeList) => {
        addedNodes.forEach((bodyNode) => {
            if (
                bodyNode instanceof HTMLElement &&
                bodyNode.matches("gen-search-widget")
            ) {
                retryFindingShadowRoot(bodyNode, 5, 500); // Retry 5 times with 500ms delay
            }
        });
    };

    const handleMutations = (mutations: MutationRecord[]) => {
        for (const mutation of mutations) {
            if (mutation.type === "childList") {
                processAddedNodes(mutation.addedNodes);
            }
        }
    };

    const observeMutations = (handleMutations: MutationCallback) => {
        const mutationObserver = new MutationObserver(handleMutations);
        const bodyElement = document.querySelector("body");
        if (bodyElement) {
            mutationObserver.observe(bodyElement, {
                childList: true,
                subtree: true,
            });
        }

        return mutationObserver;
    };

    const createWidgetDocument = () => {
        const widgetDocument =
            document.implementation.createHTMLDocument("Widget Document");
        const searchWidget = document.createElement("gen-search-widget");
        widgetDocument.body.appendChild(searchWidget);

        searchWidget.setAttribute("configId", "3cd01300-f657-4dbb-bd51-7e98d00cdc7d");

        searchWidget.setAttribute("alwaysopened", "true");
        searchWidget.setAttribute("anchorsTarget", "_blank");
        searchWidget.setAttribute("location", "eu");
        searchWidget.style.display = "none";
        searchWidget.style.height = "100%";
        searchWidget.style.width = "100%";
        searchWidget.style.position = "relative";

        return widgetDocument.documentElement.outerHTML;
    };

    useEffect(() => {
        const widgetDocumentContent = createWidgetDocument();
        setWidgetDocumentContent(widgetDocumentContent);
        const mutationObserver = observeMutations(handleMutations);
        return () => {
            mutationObserver.disconnect();
        };
        /* eslint-disable */
    }, []);
    /* eslint-enable */

    return (
        <div>
            <div dangerouslySetInnerHTML={{ __html: widgetDocumentContent }} />
        </div>
    );
};
